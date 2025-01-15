from comb import *
from tree import *

pattern = Parser()

#
# expr
#

expr = Parser()
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
tag_expr = map(seq(ignore(":"), name), lambda span, name: TagExpr(span, name))


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
    seq("[", ignore(ws), expr_list, ignore(ws), "]"),
    ArrayExpr,
)

## paren
paren = starmap(seq("(", expr, ")"), ParenExpr)
spread = starmap(seq("...", ignore(ws), expr), Spread)

fn = starmap(
    seq(
        "fn",
        ignore(ws),
        "(",
        ignore(ws),
        sep(pattern, ","),
        ignore(ws),
        ")",
        ignore(ws),
        expr,
    ),
    FnExpr,
)

atom.f = alt(integer, floating, string, id, tag_expr, array, paren, spread)
expr.f = alt(atom, fn)

#
# pattern
#

ignore_pattern = map(seq("_", opt(name)), lambda span, _: IgnorePattern(span))
id_pattern = starmap(
    seq(name, opt(ignore(ws), tag("@"), ignore(ws), pattern)),
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
    sep = map(seq(ignore(ws), ",", ignore(ws)), lambda _, sep: sep)
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
    seq("[", ignore(ws), array_pattern_items, ignore(ws), "]"),
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
