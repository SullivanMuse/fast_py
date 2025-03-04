from value import Float, Int, String, Tag
from vm import run


def value(s, val):
    assert run(s) == val, f"`run({repr(s)})` produces `{val}`"


def test_run_int():
    value("123", Int(value=123))


def test_run_float():
    value("123.456", Float(value=123.456))


def test_run_tag():
    value(":asdf", Tag(value=":asdf"))


def test_run_fn():
    value("(fn() 123)()", Int(value=123))
    value("(fn(x) x)(123)", Int(value=123))
