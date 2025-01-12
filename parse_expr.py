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


def test_integer():
    s = "1234"
    node = IntExpr(Span(s, 0, len(s)))
    assert integer(s) == Success(Span(s, len(s), len(s)), node), "Success"

    s = ""
    assert integer(s) == Error(Span(s, 0, None)), "Error"


## float
fraction = map(seq(".", dec_run), lambda span, _: span)
exponent = map(seq("e", opt("-"), dec_run), lambda span, _: span)
s = seq(dec_run, opt(fraction), opt(exponent))
floating = map(
    pred(s, lambda x: not (x[1] is None or x[2] is None)),
    lambda span, _: FloatExpr(span),
)


def test_float():
    s = "123.456e789"
    node = FloatExpr(Span(s, 0, len(s)))
    assert floating(s) == Success(Span(s, len(s), len(s)), node), "Success"

    s = "123"
    assert floating(s) == Error(Span(s, 0, None)), "Error"


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


def test_tag_expr():
    s = ":asdf"
    node = TagExpr(Span(s, 0, len(s)), Span(s, 1, len(s)))
    assert tag_expr(s) == Success(Span(s, len(s), len(s)), node), "Success"

    s = ""
    assert tag_expr(s) == Error(Span(s, 0, None)), "Error"


def test_id():
    s = "asdf"
    node = IdExpr(Span(s, 0, len(s)))
    assert id(s) == Success(Span(s, len(s), len(s)), node), "Success"

    s = "123"
    assert id(s) == Error(Span(s, 0, None)), "Error"


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


def test_string():
    s = '"asdf\\""'
    assert len(s) == 8
    assert string(s) == Success(
        Span(s, len(s), len(s)),
        StringExpr(
            span=Span(s, 0, len(s)),
            fn=None,
            items=[Span(s, 1, 7)],
            lquote=Span(s, 0, 1),
            rquote=Span(s, 7, len(s)),
        ),
    )

    s = '"asdf\\"'
    assert len(s) == 7
    assert string(s) == Error(Span(s)), "Accidentally escaped delimiter"


## array
array = starmap(
    seq("[", ignore(ws), expr_list, ignore(ws), "]"),
    ArrayExpr,
)


def test_array():
    s = "[x, y, z]"
    assert array(s) == Success(
        Span(s, len(s), len(s)),
        ArrayExpr(
            span=Span(s, 0, len(s)),
            lbracket=Span(s, 0, 1),
            items=[
                IdExpr(Span(s, 1, 2)),
                IdExpr(Span(s, 4, 5)),
                IdExpr(Span(s, 7, 8)),
            ],
            rbracket=Span(s, len(s) - 1, len(s)),
        ),
    )


## paren
paren = starmap(seq("(", expr, ")"), ParenExpr)


def test_paren():
    s = "(x)"
    assert paren(s) == Success(
        Span(s, len(s), len(s)),
        ParenExpr(
            span=Span(s, 0, len(s)),
            lpar=Span(s, 0, 1),
            inner=IdExpr(Span(s, 1, 2)),
            rpar=Span(s, 2, 3),
        ),
    )


spread = starmap(seq("...", ignore(ws), expr), Spread)


def test_spread():
    s = "...r"
    assert spread(s) == Success(
        Span(s, len(s), len(s)),
        Spread(
            span=Span(s, 0, len(s)),
            ellipsis=Span(s, 0, 3),
            inner=IdExpr(Span(s, 3, 4)),
        ),
    )


atom.f = alt(integer, floating, string, id, tag_expr, array, paren, spread)
expr.f = atom
