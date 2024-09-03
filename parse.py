from comb import *
from expr import *

expr = Parser()

dec_digits = digit.many1()
dec_run = (dec_digits * ("_" * dec_digits).many0()).span()
integer = dec_run.map(Integer)

fraction = ("." * dec_run).span()
exponent = ("e" * tag("-").opt() * dec_run).span()
floating = (
    seq(dec_run, fraction.opt(), exponent.opt())
    .pred(lambda x: not (x[1] is None and x[2] is None))
    .span()
    .map(Float)
)

name = (alpha * ("_" + alnum).many0()).span()
ident = name.map(Id)
atom = Parser()

character = pred(lambda c: c not in '\\"{}').span()
escape = (tag("\\\\") + '\\"' + "\\{" + "\\}").span()
interpolant = "{" >> ws >> expr << ws << "}"
string_item = character + escape + interpolant
string = (
    (ident.opt() * ('"' >> string_item.many0() << '"'))
    .spanned()
    .map(lambda x: String(x[1], x[0][0], x[0][1]))
)

array = ("[" >> expr.opt() << "]").spanned().map(lambda x: Array(x[1], x[0]))

range_syntax = (
    seq((atom << ws).opt(), ".." >> tag("=").opt(), (ws >> atom).opt())
    .spanned()
    .map(
        lambda x: Range(
            x[1], x[0][0], x[0][2], "clopen" if x[0][1] is None else "closed"
        )
    )
)

atom.f = ident + string + integer + floating + array

expr.f = atom


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
    assert ident(s) == (Id(Span.all(s)), Input.end(s)), "Successful parse"

    s = "Hello123"
    assert ident(s) == (Id(Span.all(s)), Input.end(s)), "Successful parse"

    s = "1234asdf"
    assert ident(s) is None, "Unsuccessful parse"


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
        Range(Span.all(s), None, Id(Span(s, len(s)-1, len(s))), "closed"),
        Input.end(s),
    ), "Range to closed"
    
    s = "..b"
    assert range_syntax(s) == (
        Range(Span.all(s), None, Id(Span(s, len(s)-1, len(s))), "clopen"),
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
        Range(Span.all(s), None, Id(Span(s, len(s)-1, len(s))), "closed"),
        Input.end(s),
    ), "Range to closed with whitespace"
    
    s = ".. b"
    assert range_syntax(s) == (
        Range(Span.all(s), None, Id(Span(s, len(s)-1, len(s))), "clopen"),
        Input.end(s),
    ), "Range to clopen with whitespace"
