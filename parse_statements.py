# project
from comb import *
from tree import *
from parse_expr import expr


statements = Parser()

expr_statment = map(
    expr, lambda span, inner: Statement(span, StatementTy.Expr, children=[inner])
)

break_statement = map("break", lambda span, _: Statement(span, StatementTy.Break))
continue_statement = map(
    "continue", lambda span, _: Statement(span, StatementTy.Continue)
)
return_statement = map(
    seq("return", opt(ignore(ws), expr)),
    lambda span, rs: Statement(
        span,
        StatementTy.Return,
        children=[rs[1]] if rs[1] is not None else [],
        tokens=[rs[0]],
    ),
)

autonomous_statement = not_implemented("autonomous_statement")
semi_statement = alt(break_statement, continue_statement, expr_statment)

loop = map(
    seq("loop", ignore(ws), "{", ignore(ws), statements, ignore(ws), "}"),
    lambda span, rs: Statement(
        span, StatementTy.Loop, children=rs[4], tokens=[rs[0], rs[2], rs[6]]
    ),
)


def test_break_statement():
    s = "break"
    assert break_statement(s) == Success(
        Span(s, len(s), len(s)), Statement(Span(s, 0, len(s)), StatementTy.Break)
    )

    s = ""
    assert break_statement(s) == Error(Span(s, 0, None))


def test_continue_statement():
    s = "continue"
    assert continue_statement(s) == Success(
        Span(s, len(s), len(s)), Statement(Span(s, 0, len(s)), StatementTy.Continue)
    )

    s = ""
    assert continue_statement(s) == Error(Span(s, 0, None))


def test_return_statement():
    s = "return"
    assert return_statement(s) == Success(
        Span(s, len(s), len(s)),
        Statement(Span(s, 0, len(s)), StatementTy.Return, tokens=[Span(s, 0, len(s))]),
    )

    s = "return x"
    assert return_statement(s) == Success(
        Span(s, len(s), len(s)),
        Statement(
            Span(s, 0, len(s)),
            StatementTy.Return,
            children=[Statement(Span(s, 7, 8), ExprTy.Id)],
            tokens=[Span(s, 0, 6)],
        ),
    )

    s = ""
    assert return_statement(s) == Error(Span(s, 0, None))


@Parser
def statements_f(s0):
    s = s0

    statements_list = []
    tokens = []
    sep = seq(ignore(ws), ";", ignore(ws))

    while True:
        # Semicolon not required
        if r := autonomous_statement(s):
            s = r.span
            statements_list.append(r.val)

            if r := sep(s):
                tokens.append(r.val[0])
                s = r.span

        # Semicolon required
        elif r := semi_statement(s):
            s = r.span
            statements_list.append(r.val)

            if r := sep(s):
                tokens.append(r.val[0])
                s = r.span
            else:
                break

        # No more valid statements
        else:
            break

    return Success(s, statements_list)


statements.f = statements_f
