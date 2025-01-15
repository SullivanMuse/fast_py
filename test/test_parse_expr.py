from parse import *


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
    assert array("[]") == Success(
        span=Span(string="[]", start=2, stop=2),
        val=ArrayExpr(
            span=Span(string="[]", start=0, stop=2),
            lbracket=Span(string="[]", start=0, stop=1),
            items=[],
            rbracket=Span(string="[]", start=1, stop=2),
        ),
    )

    assert array("[x]") == Success(
        span=Span(string="[x]", start=3, stop=3),
        val=ArrayExpr(
            span=Span(string="[x]", start=0, stop=3),
            lbracket=Span(string="[x]", start=0, stop=1),
            items=[IdExpr(span=Span(string="[x]", start=1, stop=2))],
            rbracket=Span(string="[x]", start=2, stop=3),
        ),
    )

    assert array("[x,]") == Success(
        span=Span(string="[x,]", start=4, stop=4),
        val=ArrayExpr(
            span=Span(string="[x,]", start=0, stop=4),
            lbracket=Span(string="[x,]", start=0, stop=1),
            items=[IdExpr(span=Span(string="[x,]", start=1, stop=2))],
            rbracket=Span(string="[x,]", start=3, stop=4),
        ),
    )

    assert array("[x, y]") == Success(
        span=Span(string="[x, y]", start=6, stop=6),
        val=ArrayExpr(
            span=Span(string="[x, y]", start=0, stop=6),
            lbracket=Span(string="[x, y]", start=0, stop=1),
            items=[
                IdExpr(span=Span(string="[x, y]", start=1, stop=2)),
                IdExpr(span=Span(string="[x, y]", start=4, stop=5)),
            ],
            rbracket=Span(string="[x, y]", start=5, stop=6),
        ),
    )

    assert array("[x, y, ..r]") == Error(
        span=Span(string="[x, y, ..r]", start=0, stop=None), reason=None
    )

    assert array("[x, y, ...r]") == Success(
        span=Span(string="[x, y, ...r]", start=12, stop=12),
        val=ArrayExpr(
            span=Span(string="[x, y, ...r]", start=0, stop=12),
            lbracket=Span(string="[x, y, ...r]", start=0, stop=1),
            items=[
                IdExpr(span=Span(string="[x, y, ...r]", start=1, stop=2)),
                IdExpr(span=Span(string="[x, y, ...r]", start=4, stop=5)),
                Spread(
                    span=Span(string="[x, y, ...r]", start=7, stop=11),
                    ellipsis=Span(string="[x, y, ...r]", start=7, stop=10),
                    inner=IdExpr(
                        span=Span(string="[x, y, " "...r]", start=10, stop=11)
                    ),
                ),
            ],
            rbracket=Span(string="[x, y, ...r]", start=11, stop=12),
        ),
    )

    assert array("[x, ...r,  y]") == Success(
        span=Span(string="[x, ...r,  y]", start=13, stop=13),
        val=ArrayExpr(
            span=Span(string="[x, ...r,  y]", start=0, stop=13),
            lbracket=Span(string="[x, ...r,  y]", start=0, stop=1),
            items=[
                IdExpr(span=Span(string="[x, ...r,  y]", start=1, stop=2)),
                Spread(
                    span=Span(string="[x, ...r,  y]", start=4, stop=8),
                    ellipsis=Span(string="[x, ...r,  y]", start=4, stop=7),
                    inner=IdExpr(span=Span(string="[x, ...r,  " "y]", start=7, stop=8)),
                ),
                IdExpr(span=Span(string="[x, ...r,  y]", start=11, stop=12)),
            ],
            rbracket=Span(string="[x, ...r,  y]", start=12, stop=13),
        ),
    )

    assert array("[...r,  y]") == Success(
        span=Span(string="[...r,  y]", start=10, stop=10),
        val=ArrayExpr(
            span=Span(string="[...r,  y]", start=0, stop=10),
            lbracket=Span(string="[...r,  y]", start=0, stop=1),
            items=[
                Spread(
                    span=Span(string="[...r,  y]", start=1, stop=5),
                    ellipsis=Span(string="[...r,  y]", start=1, stop=4),
                    inner=IdExpr(span=Span(string="[...r,  y]", start=4, stop=5)),
                ),
                IdExpr(span=Span(string="[...r,  y]", start=8, stop=9)),
            ],
            rbracket=Span(string="[...r,  y]", start=9, stop=10),
        ),
    )

    assert array("[...r, y,]") == Success(
        span=Span(string="[...r, y,]", start=10, stop=10),
        val=ArrayExpr(
            span=Span(string="[...r, y,]", start=0, stop=10),
            lbracket=Span(string="[...r, y,]", start=0, stop=1),
            items=[
                Spread(
                    span=Span(string="[...r, y,]", start=1, stop=5),
                    ellipsis=Span(string="[...r, y,]", start=1, stop=4),
                    inner=IdExpr(span=Span(string="[...r, y,]", start=4, stop=5)),
                ),
                IdExpr(span=Span(string="[...r, y,]", start=7, stop=8)),
            ],
            rbracket=Span(string="[...r, y,]", start=9, stop=10),
        ),
    )

    assert array("[ ...r, y, ]") == Success(
        span=Span(string="[ ...r, y, ]", start=12, stop=12),
        val=ArrayExpr(
            span=Span(string="[ ...r, y, ]", start=0, stop=12),
            lbracket=Span(string="[ ...r, y, ]", start=0, stop=1),
            items=[
                Spread(
                    span=Span(string="[ ...r, y, ]", start=2, stop=6),
                    ellipsis=Span(string="[ ...r, y, ]", start=2, stop=5),
                    inner=IdExpr(span=Span(string="[ ...r, y, " "]", start=5, stop=6)),
                ),
                IdExpr(span=Span(string="[ ...r, y, ]", start=8, stop=9)),
            ],
            rbracket=Span(string="[ ...r, y, ]", start=11, stop=12),
        ),
    )


def test_fn():
    assert fn("fn() x") == Success(
        span=Span(string="fn() x", start=6, stop=6),
        val=FnExpr(
            span=Span(string="fn() x", start=0, stop=6),
            fn_token=Span(string="fn() x", start=0, stop=2),
            lpar=Span(string="fn() x", start=2, stop=3),
            params=[],
            rpar=Span(string="fn() x", start=3, stop=4),
            inner=IdExpr(span=Span(string="fn() x", start=5, stop=6)),
        ),
    )

    assert fn("fn(x) x") == Success(
        span=Span(string="fn(x) x", start=7, stop=7),
        val=FnExpr(
            span=Span(string="fn(x) x", start=0, stop=7),
            fn_token=Span(string="fn(x) x", start=0, stop=2),
            lpar=Span(string="fn(x) x", start=2, stop=3),
            params=[
                IdPattern(
                    span=Span(string="fn(x) x", start=3, stop=4),
                    name=Span(string="fn(x) x", start=3, stop=4),
                    at_token=None,
                    inner=None,
                )
            ],
            rpar=Span(string="fn(x) x", start=4, stop=5),
            inner=IdExpr(span=Span(string="fn(x) x", start=6, stop=7)),
        ),
    )

    assert fn("fn(x,) x") == Success(
        span=Span(string="fn(x,) x", start=8, stop=8),
        val=FnExpr(
            span=Span(string="fn(x,) x", start=0, stop=8),
            fn_token=Span(string="fn(x,) x", start=0, stop=2),
            lpar=Span(string="fn(x,) x", start=2, stop=3),
            params=[
                IdPattern(
                    span=Span(string="fn(x,) x", start=3, stop=4),
                    name=Span(string="fn(x,) x", start=3, stop=4),
                    at_token=None,
                    inner=None,
                )
            ],
            rpar=Span(string="fn(x,) x", start=5, stop=6),
            inner=IdExpr(span=Span(string="fn(x,) x", start=7, stop=8)),
        ),
    )

    assert fn("fn(x,y) x") == Success(
        span=Span(string="fn(x,y) x", start=9, stop=9),
        val=FnExpr(
            span=Span(string="fn(x,y) x", start=0, stop=9),
            fn_token=Span(string="fn(x,y) x", start=0, stop=2),
            lpar=Span(string="fn(x,y) x", start=2, stop=3),
            params=[
                IdPattern(
                    span=Span(string="fn(x,y) x", start=3, stop=4),
                    name=Span(string="fn(x,y) x", start=3, stop=4),
                    at_token=None,
                    inner=None,
                ),
                IdPattern(
                    span=Span(string="fn(x,y) x", start=5, stop=6),
                    name=Span(string="fn(x,y) x", start=5, stop=6),
                    at_token=None,
                    inner=None,
                ),
            ],
            rpar=Span(string="fn(x,y) x", start=6, stop=7),
            inner=IdExpr(span=Span(string="fn(x,y) x", start=8, stop=9)),
        ),
    )

    assert fn("fn(x,y,) x") == Success(
        span=Span(string="fn(x,y,) x", start=10, stop=10),
        val=FnExpr(
            span=Span(string="fn(x,y,) x", start=0, stop=10),
            fn_token=Span(string="fn(x,y,) x", start=0, stop=2),
            lpar=Span(string="fn(x,y,) x", start=2, stop=3),
            params=[
                IdPattern(
                    span=Span(string="fn(x,y,) x", start=3, stop=4),
                    name=Span(string="fn(x,y,) x", start=3, stop=4),
                    at_token=None,
                    inner=None,
                ),
                IdPattern(
                    span=Span(string="fn(x,y,) x", start=5, stop=6),
                    name=Span(string="fn(x,y,) x", start=5, stop=6),
                    at_token=None,
                    inner=None,
                ),
            ],
            rpar=Span(string="fn(x,y,) x", start=7, stop=8),
            inner=IdExpr(span=Span(string="fn(x,y,) x", start=9, stop=10)),
        ),
    )

    assert fn("fn( x , y , ) x") == Success(
        span=Span(string="fn( x , y , ) x", start=15, stop=15),
        val=FnExpr(
            span=Span(string="fn( x , y , ) x", start=0, stop=15),
            fn_token=Span(string="fn( x , y , ) x", start=0, stop=2),
            lpar=Span(string="fn( x , y , ) x", start=2, stop=3),
            params=[
                IdPattern(
                    span=Span(string="fn( x , y , ) x", start=4, stop=5),
                    name=Span(string="fn( x , y , ) x", start=4, stop=5),
                    at_token=None,
                    inner=None,
                ),
                IdPattern(
                    span=Span(string="fn( x , y , ) x", start=8, stop=9),
                    name=Span(string="fn( x , y , ) x", start=8, stop=9),
                    at_token=None,
                    inner=None,
                ),
            ],
            rpar=Span(string="fn( x , y , ) x", start=12, stop=13),
            inner=IdExpr(span=Span(string="fn( x , y , ) x", start=14, stop=15)),
        ),
    )

    # errors:
    assert fn("") == Error(span=Span(string="", start=0, stop=None), reason=None)

    assert fn("fn()") == Error(
        span=Span(string="fn()", start=0, stop=None), reason=None
    )

    assert fn("fn(,)") == Error(
        span=Span(string="fn(,)", start=0, stop=None), reason=None
    )

    assert fn("fn(,x)") == Error(
        span=Span(string="fn(,x)", start=0, stop=None), reason=None
    )


def test_block():
    # success
    assert block("{}") == Success(
        span=Span(string="{}", start=2, stop=2),
        val=BlockExpr(
            span=Span(string="{}", start=0, stop=2),
            lbrace=Span(string="{}", start=0, stop=1),
            statements=[],
            rbrace=Span(string="{}", start=1, stop=2),
        ),
    )

    assert block("{x}") == Success(
        span=Span(string="{x}", start=3, stop=3),
        val=BlockExpr(
            span=Span(string="{x}", start=0, stop=3),
            lbrace=Span(string="{x}", start=0, stop=1),
            statements=[
                ExprStatement(
                    span=Span(string="{x}", start=1, stop=2),
                    inner=IdExpr(span=Span(string="{x}", start=1, stop=2)),
                )
            ],
            rbrace=Span(string="{x}", start=2, stop=3),
        ),
    )

    # {x;y}
    # {x;y;}
    # { x ; y ; }

    # errors
    # ""
    # {;}
    # {;x}


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
