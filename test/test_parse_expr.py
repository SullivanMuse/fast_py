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

    s = ""
    assert id(s) == Error(Span(s, 0, None)), "Error"


def test_string():
    s = '"asdf\\""'
    assert len(s) == 8
    assert string(s) == Success(
        Span(s, len(s), len(s)),
        StringExpr(
            Span(s, 0, len(s)),
            None,
            [Span(s, 1, 7)],
            [],
            Span(s, 0, 1),
            Span(s, 7, len(s)),
        ),
    )

    s = '"asdf\\"'
    assert len(s) == 7
    assert string(s) == Error(Span(s)), "Accidentally escaped delimiter"

    s = 'asdf""'
    print(f"{string(s) = }")
    assert string(s), "Error"

    assert string('""') == Success(
        span=Span(string='""', start=2, stop=2),
        val=StringExpr(
            span=Span(string='""', start=0, stop=2),
            fn=None,
            chars=[Span(string='""', start=1, stop=1)],
            interpolants=[],
            lquote=Span(string='""', start=0, stop=1),
            rquote=Span(string='""', start=1, stop=2),
        ),
    )

    assert string('"x"') == Success(
        span=Span(string='"x"', start=3, stop=3),
        val=StringExpr(
            span=Span(string='"x"', start=0, stop=3),
            fn=None,
            chars=[Span(string='"x"', start=1, stop=2)],
            interpolants=[],
            lquote=Span(string='"x"', start=0, stop=1),
            rquote=Span(string='"x"', start=2, stop=3),
        ),
    )

    assert string('"x{x}"') == Success(
        span=Span(string='"x{x}"', start=6, stop=6),
        val=StringExpr(
            span=Span(string='"x{x}"', start=0, stop=6),
            fn=None,
            chars=[
                Span(string='"x{x}"', start=1, stop=2),
                Span(string='"x{x}"', start=5, stop=5),
            ],
            interpolants=[IdExpr(span=Span(string='"x{x}"', start=3, stop=4))],
            lquote=Span(string='"x{x}"', start=0, stop=1),
            rquote=Span(string='"x{x}"', start=5, stop=6),
        ),
    )

    assert string('"x{x}x"') == Success(
        span=Span(string='"x{x}x"', start=7, stop=7),
        val=StringExpr(
            span=Span(string='"x{x}x"', start=0, stop=7),
            fn=None,
            chars=[
                Span(string='"x{x}x"', start=1, stop=2),
                Span(string='"x{x}x"', start=5, stop=6),
            ],
            interpolants=[IdExpr(span=Span(string='"x{x}x"', start=3, stop=4))],
            lquote=Span(string='"x{x}x"', start=0, stop=1),
            rquote=Span(string='"x{x}x"', start=6, stop=7),
        ),
    )

    assert string('"x{x}x{x}"') == Success(
        span=Span(string='"x{x}x{x}"', start=10, stop=10),
        val=StringExpr(
            span=Span(string='"x{x}x{x}"', start=0, stop=10),
            fn=None,
            chars=[
                Span(string='"x{x}x{x}"', start=1, stop=2),
                Span(string='"x{x}x{x}"', start=5, stop=6),
                Span(string='"x{x}x{x}"', start=9, stop=9),
            ],
            interpolants=[
                IdExpr(span=Span(string='"x{x}x{x}"', start=3, stop=4)),
                IdExpr(span=Span(string='"x{x}x{x}"', start=7, stop=8)),
            ],
            lquote=Span(string='"x{x}x{x}"', start=0, stop=1),
            rquote=Span(string='"x{x}x{x}"', start=9, stop=10),
        ),
    )

    assert string('"{x}x{x}"') == Success(
        span=Span(string='"{x}x{x}"', start=9, stop=9),
        val=StringExpr(
            span=Span(string='"{x}x{x}"', start=0, stop=9),
            fn=None,
            chars=[
                Span(string='"{x}x{x}"', start=1, stop=1),
                Span(string='"{x}x{x}"', start=4, stop=5),
                Span(string='"{x}x{x}"', start=8, stop=8),
            ],
            interpolants=[
                IdExpr(span=Span(string='"{x}x{x}"', start=2, stop=3)),
                IdExpr(span=Span(string='"{x}x{x}"', start=6, stop=7)),
            ],
            lquote=Span(string='"{x}x{x}"', start=0, stop=1),
            rquote=Span(string='"{x}x{x}"', start=8, stop=9),
        ),
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
