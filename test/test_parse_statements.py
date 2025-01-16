from parse import *


def test_label():
    s = "'label"
    assert label(s)

    s = "'x"
    assert label(s)

    # errors
    s = "'"
    assert not label(s)

    s = ""
    assert not label(s)


def test_expr_statement():
    s = "x"
    assert expr_statement(s)

    s = ""
    assert not expr_statement(s)


def test_return_statement():
    s = "return"
    assert return_statement(s)

    s = "return x"
    assert return_statement(s)

    s = ""
    assert not return_statement(s)


def test_continue_statement():
    s = "continue"
    assert continue_statement(s)

    s = "continue 'outer"
    assert continue_statement(s)

    s = ""
    assert not continue_statement(s)

    s = "'outer x"
    assert not continue_statement(s)

    s = "cont"
    assert not continue_statement(s)


def test_break_statement():
    s = "break"
    assert break_statement(s)

    s = "break 'outer"
    assert break_statement(s)

    s = "break x"
    assert break_statement(s)

    s = "break 'outer x"
    assert break_statement(s)

    s = ""
    assert not break_statement(s)

    s = "'outer x"
    assert not break_statement(s)

    s = "cont"
    assert not break_statement(s)


def test_loop_statement():
    s = ""
    assert not loop_statement(s)

    s = "loop"
    assert not loop_statement(s)

    s = "loop {"
    assert not loop_statement(s)

    s = "loop }"
    assert not loop_statement(s)

    s = "loop {}"
    assert loop_statement(s)

    s = "loop {x; y}"
    assert loop_statement(s)


def test_fn_statement():
    s = "fn name() {}"
    assert fn_statement(s)

    s = "fn name(x) {}"
    assert fn_statement(s)

    s = "fn name(x, y) {}"
    assert fn_statement(s)

    s = "fn name ( x , y , ) { }"
    assert fn_statement(s)

    s = "fn name(x, y) { x; y }"
    assert fn_statement(s)


def test_let():
    s = "let x = 5"
    assert let_statement(s)

    s = "let x=5"
    assert let_statement(s)

    # errors
    s = "let"
    assert not let_statement(s)

    s = "="
    assert not let_statement(s)

    s = "le"
    assert not let_statement(s)

    s = "let x ="
    assert not let_statement(s)


def test_assign():
    s = "x = 5"
    assert assign_statement(s)

    s = "x=5"
    assert assign_statement(s)

    # errors
    s = "let"
    assert not assign_statement(s)

    s = "="
    assert not assign_statement(s)

    s = "le"
    assert not assign_statement(s)

    s = "let x ="
    assert not assign_statement(s)
