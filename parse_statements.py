from comb import *
from parse_expr import expr
from tree import *

statements = Parser()

expr_statment = map(expr, lambda span, inner: ExprStatement(span, inner))

break_statement = map("break", lambda span, _: BreakStatement(span, None, None))
continue_statement = map("continue", lambda span, _: ContinueStatement(span, None))
return_statement = map(
    seq("return", opt(ignore(ws), expr)),
    lambda span, rs: ReturnStatement(span, rs[1]),
)

autonomous_statement = not_implemented("autonomous_statement")
semi_statement = alt(break_statement, continue_statement, expr_statment)

loop = map(
    seq("loop", ignore(ws), "{", ignore(ws), statements, ignore(ws), "}"),
    lambda span, rs: Statement(
        span, StatementTy.Loop, children=rs[4], tokens=[rs[0], rs[2], rs[6]]
    ),
)


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
