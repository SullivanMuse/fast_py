from comb import *
from tree import *

statements = Parser()
expr = Parser()
pattern = Parser()

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
floating = map(
    pred(s, lambda x: not (x[1] is None or x[2] is None)),
    lambda span, _: FloatExpr(span),
)

## id
keywords = alt(
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
block = starmap(seq("{", ignore(ws), statements, ignore(ws), "}"), BlockExpr)

atom.f = alt(integer, floating, string, id, tag_expr, array, paren, spread, block, fn)

expr.f = alt(atom)

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
float_pattern = not_implemented("float_pattern")
string_pattern = not_implemented("string_pattern")
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

expr_statment = map(seq(expr), lambda span, inner: ExprStatement(span, None, inner))

# break_statement = map("break", lambda span, _: BreakStatement(span, None, None))
# continue_statement = map("continue", lambda span, _: ContinueStatement(span, None))
# return_statement = map(
#     seq("return", opt(ws, expr)),
#     lambda span, rs: ReturnStatement(span, rs[1]),
# )

loop_expr = starmap(
    seq("loop", ignore(ws), "{", ignore(ws), statements, ignore(ws), "}"), LoopExpr
)

semi_optional = not_implemented("autonomous_statement")
semi_required = alt(expr_statment)


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
