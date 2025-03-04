from value import Int
from vm import run


def value(s, val):
    assert run(s) == val, f"`run({repr(s)})` produces `{val}`"


def test_run_int():
    value("123", Int(value=123))


def test_run_fn():
    value("(fn() 123)()", Int(value=123))
    # value("(fn(x) x)(123)", Int(value=123))
