from comb import *
from expr import *

expr = Parser()

run = digit.many1()
integer = (run * ("_" * run).many0()).span().map(Integer)
name = (alpha * alnum.many0().optional() * ("_" * alnum.many1()).many0()).span()
ident = name.map(Id)
atom = ident + integer


def test_integer():
    s = "1234"
    assert integer(s) == (Integer(Span.all(s)), Input.end(s)), "Successful parse"

    s = "123_456"
    assert integer(s) == (Integer(Span.all(s)), Input.end(s)), "Successful parse"

    s = "_123"
    assert integer(s) is None, "Unsuccesful parse"

    s = ""
    assert integer(s) is None, "Unsuccesful parse"


def test_ident():
    s = "asdf"
    assert ident(s) == (Id(Span.all(s)), Input.end(s)), "Successful parse"

    s = "Hello123"
    assert ident(s) == (Id(Span.all(s)), Input.end(s)), "Successful parse"

    s = "1234asdf"
    assert ident(s) is None, "Unsuccessful parse"
