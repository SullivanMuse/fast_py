from comb import Input, Span
from expr import *
from parse import *

def test_integer():
    s = "1234"
    assert integer(s) == (Integer(Span.all(s)), Input.end(s)), "Successful parse"

    s = "123_456"
    assert integer(s) == (Integer(Span.all(s)), Input.end(s)), "Successful parse"

    s = "_123"
    assert integer(s) is None, "Unsuccesful parse"

    s = ""
    assert integer(s) is None, "Unsuccesful parse"


def test_float():
    s = "1234"
    assert floating(s) is None, "Unsuccessful parse"

    s = "1.0"
    assert floating(s) == (Float(Span.all(s)), Input.end(s)), "Successful parse"

    s = "1e5"
    assert floating(s) == (Float(Span.all(s)), Input.end(s)), "Successful parse"

    s = "1.0e-5"
    assert floating(s) == (Float(Span.all(s)), Input.end(s)), "Successful parse"


def test_ident():
    s = "asdf"
    assert id(s) == (Id(Span.all(s)), Input.end(s)), "Successful parse"

    s = "Hello123"
    assert id(s) == (Id(Span.all(s)), Input.end(s)), "Successful parse"

    s = "1234asdf"
    assert id(s) is None, "Unsuccessful parse"


def test_string():
    s = '"Hello"'
    assert string(s) == (
        String(
            Span.all(s),
            None,
            [
                Span(s, 1, 2),
                Span(s, 2, 3),
                Span(s, 3, 4),
                Span(s, 4, 5),
                Span(s, 5, 6),
            ],
        ),
        Input.end(s),
    ), "Basic string"

    s = 'd"2024-09-01"'
    assert string(s) == (
        String(
            Span.all(s),
            Id(Span(s, 0, 1)),
            [
                Span(s, 2, 3),
                Span(s, 3, 4),
                Span(s, 4, 5),
                Span(s, 5, 6),
                Span(s, 6, 7),
                Span(s, 7, 8),
                Span(s, 8, 9),
                Span(s, 9, 10),
                Span(s, 10, 11),
                Span(s, 11, 12),
            ],
        ),
        Input.end(s),
    ), "String with modifier"

    s = '"Hello, {there}"'
    assert string(s) == (
        String(
            Span.all(s),
            None,
            [
                Span(s, 1, 2),
                Span(s, 2, 3),
                Span(s, 3, 4),
                Span(s, 4, 5),
                Span(s, 5, 6),
                Span(s, 6, 7),
                Span(s, 7, 8),
                Id(Span(s, 9, 14)),
            ],
        ),
        Input.end(s),
    ), "String with interpolant"

    s = '"Hello\\\\!"'
    assert string(s) == (
        String(
            Span.all(s),
            None,
            [
                Span(s, 1, 2),
                Span(s, 2, 3),
                Span(s, 3, 4),
                Span(s, 4, 5),
                Span(s, 5, 6),
                Span(s, 6, 8),
                Span(s, 8, 9),
            ],
        ),
        Input.end(s),
    ), "String with escape"


def test_array():
    s = "[]"
    assert array(s) == (
        Array(Span.all(s), None),
        Input.end(s),
    ), "Array with no elements"

    s = "[1]"
    assert array(s) == (
        Array(
            Span.all(s),
            Integer(Span(s, 1, 2)),
        ),
        Input.end(s),
    ), "Array with single element"

    # TODO:
    #   s = "[1, 2]"
    #   s = "[1, 2,]"


def test_range():
    s = ".."
    assert range_syntax(s) == (
        Range(Span.all(s), None, None, "clopen"),
        Input.end(s),
    ), "Range all clopen"

    s = "..="
    assert range_syntax(s) == (
        Range(Span.all(s), None, None, "closed"),
        Input.end(s),
    ), "Range all closed"

    s = "a..="
    assert range_syntax(s) == (
        Range(Span.all(s), Id(Span(s, 0, 1)), None, "closed"),
        Input.end(s),
    ), "Range from closed"

    s = "a.."
    assert range_syntax(s) == (
        Range(Span.all(s), Id(Span(s, 0, 1)), None, "clopen"),
        Input.end(s),
    ), "Range from clopen"

    s = "..=b"
    assert range_syntax(s) == (
        Range(Span.all(s), None, Id(Span(s, len(s) - 1, len(s))), "closed"),
        Input.end(s),
    ), "Range to closed"

    s = "..b"
    assert range_syntax(s) == (
        Range(Span.all(s), None, Id(Span(s, len(s) - 1, len(s))), "clopen"),
        Input.end(s),
    ), "Range to clopen"

    s = " .."
    assert range_syntax(s) is None, "Bad whitespace"

    s = " ..="
    assert range_syntax(s) is None, "Bad whitespace"

    s = "a ..="
    assert range_syntax(s) == (
        Range(Span.all(s), Id(Span(s, 0, 1)), None, "closed"),
        Input.end(s),
    ), "Range from closed with whitespace"

    s = "a .."
    assert range_syntax(s) == (
        Range(Span.all(s), Id(Span(s, 0, 1)), None, "clopen"),
        Input.end(s),
    ), "Range from clopen with whitespace"

    s = "..= b"
    assert range_syntax(s) == (
        Range(Span.all(s), None, Id(Span(s, len(s) - 1, len(s))), "closed"),
        Input.end(s),
    ), "Range to closed with whitespace"

    s = ".. b"
    assert range_syntax(s) == (
        Range(Span.all(s), None, Id(Span(s, len(s) - 1, len(s))), "clopen"),
        Input.end(s),
    ), "Range to clopen with whitespace"


def test_fn():
    s = "fn(a,b,c) a"
    assert fn(s) == (
        Fn(
            Span.all(s),
            [Span(s, 3, 4), Span(s, 5, 6), Span(s, 7, 8)],
            Id(Span(s, len(s) - 1, len(s))),
        ),
        Input.end(s),
    ), "Successful parse"

    s = "fn ( a , b , c , ) a"
    assert fn(s) == (
        Fn(
            Span.all(s),
            [Span(s, 5, 6), Span(s, 9, 10), Span(s, 13, 14)],
            Id(Span(s, len(s) - 1, len(s))),
        ),
        Input.end(s),
    ), "Successful parse"


def test_paren():
    s = "(x)"
    assert paren(s) == (
        Paren(Span.all(s), Id(Span(s, 1, 2))),
        Input.end(s),
    ), "Successful parse"

    s = "( x )"
    assert paren(s) == (
        Paren(Span.all(s), Id(Span(s, 2, 3))),
        Input.end(s),
    ), "Successful parse"

    s = "( (x) )"
    assert paren(s) == (
        Paren(Span.all(s), Paren(Span(s, 2, 5), Id(Span(s, 3, 4)))),
        Input.end(s),
    ), "Successful parse"


def test_postfix1():
    s = "x.y(a)[c].await.chain?"
    id_x = Id(Span(s, i=0, j=1))
    field_y = Field(Span(s, i=0, j=3), id_x, Span(s, i=2, j=3))
    call = Call(Span(s, i=0, j=6), field_y, Id(Span(s, i=4, j=5)))
    index = Index(Span(s, i=0, j=9), call, Id(Span(s, i=7, j=8)))
    await_ = Await(Span(s, i=0, j=15), index)
    chain = Chain(Span(s, i=0, j=21), await_)
    propogate = Propogate(Span(s, i=0, j=22), chain)
    assert postfix1(s) == (
        propogate,
        Input.end(s),
    ), "Successful parse"


def test_prefix_parsers():
    s = "...!~-:x"
    id_x = Id(Span(s, i=7, j=8))
    quote = Prefix(Span(s, i=6, j=8), ":", id_x)
    negative = Prefix(Span(s, i=5, j=8), "-", quote)
    complement = Prefix(Span(s, i=4, j=8), "~", negative)
    not_ = Prefix(Span(s, i=3, j=8), "!", complement)
    spread = Prefix(Span.all(s), "...", not_)
    assert prefix1(s) == (spread, Input.end(s)), "Successful parse"