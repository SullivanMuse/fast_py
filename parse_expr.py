from comb import *
from tree import *

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
escape = seq("\\", alt("\\", '"', "{", "}"))
forbidden = set(r"\"{}")
regular = pred(one, lambda s: s.str() not in forbidden)
interpolant = map(seq(ignore("{"), expr, ignore("}")), lambda _, item: item)
piece = map(many0(alt(regular, escape)), lambda span, _: span)
string_impl = seq('"', many0(piece, interpolant), piece, '"')
string = starmap(
    string_impl,
    lambda span, lquote, pieces, piece, rquote: StringExpr(
        span,
        fn=None,
        items=[*pieces, piece],
        lquote=lquote,
        rquote=rquote,
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

atom.f = alt(integer, floating, string, id, tag_expr, array, paren, spread)
expr.f = atom
