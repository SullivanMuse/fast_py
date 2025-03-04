from parse import *
from tree import *


def parses_to(s, cls):
    result = statement(s)
    assert result, f"`{s}` parses"
    assert type(result.val) is cls, f"`{s}` has type `{cls.__name__}`"


def fails_parse(s):
    assert not statement(s), f"`{s}` fails to parse"


def test_label():

    s = "'label"
    assert label(s)

    s = "'x"
    assert label(s)

    # errors
    fails_parse("'")
    fails_parse("")


def test_expr_statement():
    parses_to("x", ExprStatement)
    fails_parse("")


def test_return_statement():
    parses_to("return", ReturnStatement)
    parses_to("return x", ReturnStatement)
    fails_parse("")


def test_continue_statement():
    parses_to("continue", ContinueStatement)
    parses_to("continue 'outer", ContinueStatement)
    fails_parse("")
    fails_parse("'outer x")


def test_break_statement():
    parses_to("break", BreakStatement)
    parses_to("break 'outer", BreakStatement)
    parses_to("break 'outer x", BreakStatement)
    fails_parse("")
    fails_parse("'outer x")


def test_loop_statement():
    fails_parse("")
    fails_parse("loop")
    fails_parse("loop {")
    fails_parse("loop }")
    parses_to("loop {}", LoopStatement)
    parses_to("loop {x; y}", LoopStatement)


def test_match_statement():
    fails_parse("")
    fails_parse("match")
    fails_parse("match {")
    fails_parse("match }")
    parses_to("match x {}", MatchStatement)
    parses_to("match x { x -> x , x -> y }", MatchStatement)
    parses_to("match x{x->x,x->y}", MatchStatement)


def test_fn_statement():
    parses_to("fn name() {}", FnStatement)
    parses_to("fn name(x) {}", FnStatement)
    parses_to("fn name(x, y) {}", FnStatement)
    parses_to("fn name ( x , y , ) { }", FnStatement)
    parses_to("fn name(x, y) { x; y }", FnStatement)


def test_let():
    parses_to("let x = 5", LetStatement)
    parses_to("let x=5", LetStatement)
    fails_parse("let")
    fails_parse("=")
    fails_parse("")
    fails_parse("let x =")


def test_assign():
    parses_to("x=5", AssignStatement)
    parses_to("x = 5", AssignStatement)
    fails_parse("let")
    fails_parse("=")
