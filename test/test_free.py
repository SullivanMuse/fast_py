from tree import *
from parse import expr, pattern, statement


# ====================
# exprs
# ====================


def expr_no_free(e):
    assert set(expr(e).val.free()) == set(), f"`{e}` has no free variables"


def expr_has_free(e, free, depth=1):
    assert set(expr(e).val.free()) == set(
        free
    ), f"`{e}` has free variables {sorted(set(free))}"
    if depth != 0:
        expr_has_free(f"({e})", free, depth=depth - 1)


def test_int_expr_free():
    expr_no_free("123")


def test_tag_expr_free():
    expr_no_free(":asdf")


def test_float_expr_free():
    expr_no_free("123.456e789")


def test_string_expr_free():
    expr_has_free('f"{x}y"', {"f", "x"})


def test_array_expr_free():
    expr_has_free("[1, 2, x, ...xs]", {"x", "xs"})


def test_call_expr_free():
    expr_has_free("f(x, y)", {"f", "x", "y"})


def test_index_expr_free():
    expr_has_free("f[x, y]", {"f", "x", "y"})


def test_binary_expr_free():
    # TODO: uncomment after implementing unary expressions
    # has_free_vars("x + y", {"x", "y"})
    pass


def test_unary_expr_free():
    # TODO: uncomment after implementing unary expressions
    # has_free_vars("!x", {"x"})
    pass


def test_comparison_expr_free():
    # TODO: uncomment after implementing comparison expressions
    # has_free_vars("x in y <= z", {"x", "y", "z"})
    pass


def test_id_expr_free():
    expr_has_free("x", {"x"})


def test_fn_expr_free():
    expr_has_free("fn(f, x) { f(x, y); }", {"y"})


def test_block_expr_free():
    expr_has_free("{let x = 1; f(x); y;}", {"f", "y"})


def test_match_expr_free():
    expr_has_free("match x { y -> { y; x; } }", {"x"})


def test_loop_expr_free():
    expr_has_free("loop { x; y; }", {"x", "y"})


# ====================
# patterns
# ====================


def pattern_binds(p, vars=None):
    if not vars:
        assert not set(pattern(p).val.bound()), f"`{p}` binds nothing"
    else:
        assert set(pattern(p).val.bound()) == vars, f"`{p}` binds {sorted(set(vars))}"


def test_ignore_pattern_bound():
    pattern_binds("_")
    pattern_binds("_xyz")


def test_id_pattern_bound():
    pattern_binds("x", {"x"})
    pattern_binds("x@y", {"x", "y"})


def test_tag_pattern_bound():
    pattern_binds(":asdf")


def test_int_pattern_bound():
    pattern_binds("123")


def test_float_pattern_bound():
    pattern_binds("123.456e789")


def test_string_pattern_bound():
    pattern_binds('"hello"')


def test_array_pattern_bound():
    pattern_binds("[1, 2, x, ...xs]", {"x", "xs"})


# ====================
# statements
# ====================


def statement_early_binds(s, vars=None):
    if not vars:
        assert not set(statement(s).val.early_bound()), f"`{s}` early binds nothing"
    else:
        assert set(statement(s).val.early_bound()) == vars, f"`{s}` early binds {sorted(set(vars))}"


def statement_binds(s, vars=None):
    if not vars:
        assert not set(statement(s).val.bound()), f"`{s}` binds nothing"
    else:
        assert set(statement(s).val.bound()) == vars, f"`{s}` binds {sorted(set(vars))}"


def statement_free(s, vars=None):
    if not vars:
        assert not set(statement(s).val.free()), f"`{s}` has no free variables"
    else:
        assert set(statement(s).val.free()) == vars, f"`{s}` has free variables {sorted(set(vars))}"


def test_expr_statement_free_bound():
    statement_binds("x")
    statement_early_binds("x")
    statement_free("x", {"x"})


def test_fn_statement_free_bound():
    statement_binds("fn f() {}")
    statement_free("fn f(x) {f(x); y;}", {"y"})
    statement_early_binds("fn f() {}", {"f"})


def test_let_statement_free_bound():
    statement_binds("let x = 1", {"x"})
    statement_early_binds("let x = 1")
    statement_free("let x = y", {"y"})


def test_assign_statement_free_bound():
    statement_binds("x = 1")
    statement_early_binds("x = 1")
    statement_free("x = 1")
