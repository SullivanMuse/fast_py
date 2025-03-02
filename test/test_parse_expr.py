from parse import *


def expr_test(fn, passing, failing):
    """Factory function for creating a bunch of expression parsing assertions"""
    for s in passing:
        assert fn(s), f"{fn.__name__} should parse {repr(s)}"
        assert expr(s), f"{expr.__name__} should parse {repr(s)}"

    for s in failing:
        assert not fn(s), f"{f.__name__} should not parse {repr(s)}"


def test_integer():
    expr_test(
        integer,
        ["1234"],
        [""],
    )


def test_float():
    expr_test(float_expr, ["123.456e789", "123.456"], ["123"])


def test_tag_expr():
    expr_test(
        tag_expr,
        [":asdf"],
        [""],
    )


def test_id():
    expr_test(
        id,
        ["asdf"],
        ["123", ""],
    )


def test_string():
    expr_test(
        string,
        [
            '"asdf\\""',
            'asdf""',
            '""',
            '"x"',
            '"x{x}"',
            '"x{x}x"',
            '"x{x}x{x}"',
            '"{x}x{x}"',
        ],
        ['"asdf\\"'],
    )


def test_array():
    expr_test(
        array,
        [
            "[]",
            "[x]",
            "[x,]",
            "[x, y]",
            "[x, y, ...r]",
            "[x, ...r,  y]",
            "[...r,  y]",
            "[...r, y,]",
            "[ ...r, y, ]",
        ],
        ["[x, y, ..r]"],
    )


def test_fn():
    expr_test(
        fn,
        ["fn() x", "fn(x) x", "fn(x,) x", "fn(x,y) x", "fn(x,y,) x", "fn( x , y , ) x"],
        ["", "fn()", "fn(,)", "fn(,x)"],
    )


def test_call():
    expr_test(
        call,
        [
            "f()",
            "f(x, y, z)",
            "f(x, y, z,)",
            "f ( x , y , z , )",
        ],
        ["", "f", "f f"],
    )


def test_index():
    expr_test(
        index,
        [
            "f[]",
            "f[x, y, z]",
            "f[x, y, z,]",
            "f [ x , y , z , ]",
        ],
        ["", "f", "f f"],
    )


def test_loop_expr():
    expr_test(
        loop_expr,
        ["loop {}", "loop {x; y}"],
        ["", "loop", "loop {", "loop }"],
    )


def test_match_expr():
    expr_test(
        match_expr,
        ["match x {}", "match x { x -> x , x -> y }", "match x{x->x,x->y}"],
        ["", "match", "match {", "match }"],
    )


def test_block():
    expr_test(
        block,
        ["{}", "{x}", "{x;y}", "{x;y;}", "{ x ; y ; }"],
        ["", "{;}", "{;x}"],
    )


def test_paren():
    expr_test(paren, ["(x)"], [])


def test_spread():
    expr_test(spread, ["...r"], [])
