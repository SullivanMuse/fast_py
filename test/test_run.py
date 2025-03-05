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


def test_run_string():
    value('"asdf"', String(value="asdf"))
    value('let f = fn(x) x; f("hello")', String(value="hello"))
    value('let f = fn(x) x; f"hello"', String(value="hello"))
    assert run('let f = fn(x) x; f"hello"') == run('let f = fn(x) x; f("hello")')


def test_run_let_statement():
    value("let f = fn(x) x; f(123)", Int(value=123))


def test_run_fn():
    value("(fn() 123)()", Int(value=123))
    value("(fn(x) x)(123)", Int(value=123))
