from comb import *
from expr import *
from pprint import pprint

from parse_expr import expr


break_statement = integer = map("break", lambda span, _: Node(span, Statement.Break))

autonomous_statement = alt("")
semi_statement = alt(break_statement, expr)


@Parser
def statements(s0):
    s = s0

    statements_list = []
    tokens = []

    while True:
        # Semicolon not required
        if r := autonomous_statement(s):
            s = r.span
            statements_list.append(r.val)

            if r := seq(ignore(ws), ";", ignore(ws)):
                tokens.append(r.val[0])
                s = r.span

        # Semicolon required
        elif r := semi_statement(s):
            s = r.span
            statements_list.append(r.val)

            if r := seq(ignore(ws), ";", ignore(ws)):
                tokens.append(r.val[0])
                s = r.span
            else:
                break

        # No more valid statements
        else:
            break

    return Success(s, statements_list)
