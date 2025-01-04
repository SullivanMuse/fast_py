# project
from comb import *
from tree import *
from parse_expr import expr


statements = Parser()

expr_statment = map(expr, lambda span, inner: Node(span, Statement.Expr, children=[inner]))

break_statement = map("break", lambda span, _: Node(span, Statement.Break))
continue_statement = map("continue", lambda span, _: Node(span, Statement.Continue))
return_statement = map(seq("return", opt(ignore(ws), expr)), lambda span, rs: Node(span, Statement.Return, children=[rs[1]] if rs[1] is not None else [], tokens=[rs[0]]))

autonomous_statement = not_implemented("autonomous_statement")
semi_statement = alt(break_statement, continue_statement, expr_statment)

loop = map(seq("loop", ignore(ws), "{", ignore(ws), statements, ignore(ws), "}"), lambda span, rs: Node(span, Statement.Loop, children=rs[4], tokens=[rs[0], rs[2], rs[6]]))

def test_break_statement():
    s = "break"
    assert break_statement(s) == Success(Span(s, len(s), len(s)), Node(Span(s, 0, len(s)), Statement.Break))

    s = ""
    assert break_statement(s) == Error(Span(s, 0, None))


def test_continue_statement():
    s = "continue"
    assert continue_statement(s) == Success(Span(s, len(s), len(s)), Node(Span(s, 0, len(s)), Statement.Continue))

    s = ""
    assert continue_statement(s) == Error(Span(s, 0, None))


def test_return_statement():
    s = "return"
    assert return_statement(s) == Success(Span(s, len(s), len(s)), Node(Span(s, 0, len(s)), Statement.Return, tokens=[Span(s, 0, len(s))]))

    s = "return x"
    assert return_statement(s) == Success(Span(s, len(s), len(s)), Node(Span(s, 0, len(s)), Statement.Return, children=[Node(Span(s, 7, 8), Expr.Id)], tokens=[Span(s, 0, 6)]))

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
