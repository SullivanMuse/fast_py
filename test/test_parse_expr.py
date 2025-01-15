from parse_expr import *


def test_integer():
    s = "1234"
    node = IntExpr(Span(s, 0, len(s)))
    assert integer(s) == Success(Span(s, len(s), len(s)), node), "Success"

    s = ""
    assert integer(s) == Error(Span(s, 0, None)), "Error"


def test_float():
    s = "123.456e789"
    node = FloatExpr(Span(s, 0, len(s)))
    assert floating(s) == Success(Span(s, len(s), len(s)), node), "Success"

    s = "123"
    assert floating(s) == Error(Span(s, 0, None)), "Error"


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
