from parse_statements import *


def test_break_statement():
    s = "break"
    assert break_statement(s) == Success(
        Span(s, len(s), len(s)), BreakStatement(Span(s, 0, len(s)), None, None)
    )

    s = ""
    assert break_statement(s) == Error(Span(s, 0, None))


def test_continue_statement():
    s = "continue"
    assert continue_statement(s) == Success(
        Span(s, len(s), len(s)), ContinueStatement(Span(s, 0, len(s)), None)
    )

    s = ""
    assert continue_statement(s) == Error(Span(s, 0, None))


def test_return_statement():
    s = "return"
    assert return_statement(s) == Success(
        Span(s, len(s), len(s)),
        ReturnStatement(Span(s, 0, len(s)), None),
    )

    s = "return x"
    assert return_statement(s) == Success(
        Span(s, len(s), len(s)),
        ReturnStatement(Span(s, 0, len(s)), IdExpr(Span(s, 7, 8))),
    )

    s = ""
    assert return_statement(s) == Error(Span(s, 0, None))
