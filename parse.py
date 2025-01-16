from comb import *
from tree import *

statements = Parser()
expr = Parser()
pattern = Parser()

#
# common
#

keywords = alt(
    "let",
    "if",
    "else",
    "use",
    "fn",
    "await",
    "chain",
    "loop",
    "while",
    "for",
    "repeat",
    "break",
    "continue",
    "return",
    "and",
    "or",
    "in",
    "notin",
    "isnot",
    "is",
)
name = map(
    seq(neg(keywords), many1(alpha), many0("_", many1(alnum))), lambda span, _: span
)
label = map(seq("'", name), lambda span, _: span)

#
# expr
#

expr_list = sep(expr, ",")

# atom
atom = Parser()

## integer
dec_digits = many1(digit)
dec_run = map(seq(dec_digits, many0("_", dec_digits)), lambda span, _: span)
integer = map(dec_run, lambda span, _: IntExpr(span))

## float
fraction = map(seq(".", dec_run), lambda span, _: span)
exponent = map(seq("e", opt("-"), dec_run), lambda span, _: span)
s = seq(dec_run, opt(fraction), opt(exponent))
float_expr = map(
    pred(s, lambda x: not (x[1] is None or x[2] is None)),
    lambda span, _: FloatExpr(span),
)

## id
id = map(name, lambda span, _: IdExpr(span))
tag_expr = map(seq(ignore(":"), name), lambda span, _: TagExpr(span))


## string
def unzip(xys):
    xs = []
    ys = []
    for i, item in enumerate(xys):
        if i % 2 == 0:
            xs.append(item)
        else:
            ys.append(item)
    return xs, ys


escape = seq("\\", alt("\\", '"', "{", "}"))
forbidden = set(r"\"{}")
regular = pred(one, lambda s: s.str() not in forbidden)
interpolant = map(seq(ignore("{"), expr, ignore("}")), lambda _, item: item)
piece = map(many0(alt(regular, escape)), lambda span, _: span)
string_impl = seq(opt(id), '"', many0(piece, interpolant), piece, '"')
string = starmap(
    string_impl,
    lambda span, fn, lquote, pieces, piece, rquote: StringExpr(
        span,
        fn,
        *unzip([*[item for sublist in pieces for item in sublist], piece]),
        lquote,
        rquote,
    ),
)

call = starmap(seq(atom, ws, "(", ws, sep(expr, ","), ws, ")"), CallExpr)
index = starmap(seq(atom, ws, "[", ws, sep(expr, ","), ws, "]"), IndexExpr)

## array
array = starmap(
    seq("[", ws, expr_list, ws, "]"),
    ArrayExpr,
)

## paren
paren = starmap(seq("(", expr, ")"), ParenExpr)
spread = starmap(seq("...", ws, expr), Spread)

fn = starmap(
    seq(
        "fn",
        ws,
        "(",
        ws,
        sep(pattern, ","),
        ws,
        ")",
        ws,
        expr,
    ),
    FnExpr,
)
block = starmap(seq("{", ws, statements, ws, "}"), BlockExpr)

arm = starmap(seq(pattern, ws, "->", ws, expr), Arm)
match_expr = starmap(
    seq("match", ws, expr, ws, "{", ws, sep(arm, ","), ws, "}"), MatchExpr
)
loop_expr = starmap(seq("loop", ws, "{", ws, statements, ws, "}"), LoopExpr)

atom.f = alt(integer, float_expr, string, id, tag_expr, array, paren, spread, block, fn)

expr.f = alt(atom, call, index)

#
# pattern
#

ignore_pattern = map(seq("_", opt(name)), lambda span, _: IgnorePattern(span))
id_pattern = starmap(
    seq(name, opt(ws, tag("@"), ws, pattern)),
    lambda span, name, rest: (
        IdPattern(span, name) if rest is None else IdPattern(span, name, *rest)
    ),
)
tag_pattern = map(seq(ignore(":"), name), lambda span, _: TagPattern(span))
integer_pattern = map(dec_run, lambda span, _: IntPattern(span))
float_pattern = map(
    pred(s, lambda x: not (x[1] is None or x[2] is None)),
    lambda span, _: FloatPattern(span),
)

string_pattern_impl = seq('"', piece, '"')
string_pattern = starmap(
    string_pattern_impl,
    StringPattern,
)

gather_pattern = starmap(
    seq("...", opt(pattern)),
    GatherPattern,
)


@Parser
def array_pattern_items(s0):
    sep = map(seq(ws, ",", ws), lambda _, sep: sep)
    s = s0

    items = []
    commas = []

    item = alt(pattern, gather_pattern)
    while r := item(s):
        s = r.span
        items.append(r.val)
        if not (r := sep(s)):
            break
        s = r.span
        commas.append(r.val)

    gather_count = sum(1 for item in items if isinstance(item, GatherPattern))
    if gather_count not in (0, 1):
        return Fail(s0.span(s), "Too many gather patterns")

    gather_index = 0
    for item in items:
        if isinstance(item, GatherPattern):
            break
        gather_index += 1
    else:
        gather_index = None

    return Success(s, (items, commas))


array_pattern = starmap(
    seq("[", ws, array_pattern_items, ws, "]"),
    lambda span, lsq, items, rsq: ArrayPattern(
        span,
        items[0],
        lsq,
        items[1],
        rsq,
    ),
)

pattern.f = alt(
    ignore_pattern,
    id_pattern,
    tag_pattern,
    integer_pattern,
    float_pattern,
    string_pattern,
    array_pattern,
    gather_pattern,
)

#
# statements
#

# semi optional
loop_statement = map(loop_expr, lambda span, inner: LoopStatement(span, None, inner))
fn_statement = starmap(
    seq(
        "fn",
        ws,
        name,
        ws,
        "(",
        ws,
        sep(pattern, ","),
        ws,
        ")",
        ws,
        "{",
        ws,
        statements,
        ws,
        "}",
    ),
    lambda span, *rest: FnStatement(span, None, *rest),
)
match_statement = map(match_expr, lambda span, inner: MatchStatement(span, None, inner))

# semi required
expr_statement = map(expr, lambda span, inner: ExprStatement(span, None, inner))
return_statement = starmap(
    seq("return", opt(ws, expr)),
    lambda span, *rest: ReturnStatement(span, None, *rest),
)
continue_statement = starmap(
    seq("continue", opt(ws, label)),
    lambda span, *rest: ContinueStatement(span, None, *rest),
)
break_statement = starmap(
    seq("break", opt(ws, label), opt(ws, expr)),
    lambda span, *rest: BreakStatement(span, None, *rest),
)
let_statement = starmap(
    seq("let", ws, pattern, ws, "=", ws, expr),
    lambda span, *rest: LetStatement(span, None, *rest),
)
assign_statement = starmap(
    seq(pattern, ws, "=", ws, expr),
    lambda span, *rest: AssignStatement(span, None, *rest),
)

semi_optional = alt(
    fn_statement,
    loop_statement,
    match_statement,
)
semi_required = alt(
    expr_statement,
    return_statement,
    continue_statement,
    break_statement,
    let_statement,
    assign_statement,
)


@Parser
def statements_f(s):
    results = []
    sep = seq(ws, ";")

    while True:
        # Get span without leading whitespace
        s1 = ws(s).span

        # Semicolon not required
        if r1 := semi_optional(s1):
            s = r1.span
            results.append(r1.val)

            if r2 := sep(s):
                r1.val.semi_token = r2.val
                s = r2.span

        # Semicolon required
        elif r1 := semi_required(s1):
            s = r1.span
            results.append(r1.val)

            if r2 := sep(s):
                r1.val.semi_token = r2.val
                s = r2.span
            else:
                break

        # No more valid statements
        else:
            break

    return Success(s, results)


statements.f = statements_f
