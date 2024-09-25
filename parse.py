from comb import *
from expr import *

expr = Parser()
expr_list = Parser()
statements = Parser()

# atom
basic = Parser()

## integer
dec_digits = many1(digit)
dec_run = map(seq(dec_digits, many0("_", dec_digits)), lambda span, _: span)
integer = map(dec_run, lambda span, _: Node(span, Expr.Int))


def test_integer():
    s = "1234"
    node = Node(Span(s, 0, len(s)), Expr.Int)
    assert integer(s) == Success(Span(s, len(s), len(s)), node), "Success"
    
    s = ""
    assert integer(s) == Error(Span(s, 0, None)), "Error"


# ## float
fraction = map(seq(".", dec_run), lambda span, _: span)
exponent = map(seq("e", opt("-"), dec_run), lambda span, _: span)
s = seq(dec_run, opt(fraction), opt(exponent))
floating = map(pred(s, lambda x: not (x[1] is None or x[2] is None)), lambda span, _: Node(span, Expr.Float))


def test_float():
    s = "123.456e789"
    node = Node(Span(s, 0, len(s)), Expr.Float)
    assert floating(s) == Success(Span(s, len(s), len(s)), node), "Success"
    
    s = "123"
    assert floating(s) == Error(Span(s, 0, None)), "Error"


## id
keywords = alt("if", "else", "use", "fn", "await", "chain", "loop", "while", "for", "repeat", "break", "continue", "return", "and", "or", "in", "notin", "isnot", "is")
name = seq(neg(keywords), many1(alpha), many0("_", many1(alnum)))
id = map(name, lambda span, _: Node(span, Expr.Id))


def test_id():
    s = "asdf"
    node = Node(Span(s, 0, len(s)), Expr.Id)
    assert id(s) == Success(Span(s, len(s), len(s)), node), "Success"
    
    s = "123"
    assert id(s) == Error(Span(s, 0, None)), "Error"


## string
escape = seq("\\", alt("\\", "\"", "{", "}"))
forbidden = set(r'\"{}')
regular = pred(one, lambda s: s.str() not in forbidden)
interpolant = map(seq(ignore("{"), expr, ignore("}")), lambda _, item: item)
piece = map(many0(alt(regular, escape)), lambda span, _: span)
string_impl = seq(ignore('"'), many0(piece, interpolant), piece, ignore('"'))
string = starmap(string_impl, lambda span, pis, piece: Node(span, Expr.String, children=[i for _, i in pis], tokens=[*(p for p, _ in pis), piece]))


def test_string():
    s = '"asdf\\""'
    assert len(s) == 8
    assert string(s) == Success(Span(s, len(s), len(s)), Node(Span(s, 0, len(s)), Expr.String, children=[], tokens=[Span(s, 1, 7)]))
    
    s = '"asdf\\"'
    assert len(s) == 7
    assert string(s) == Error(Span(s)), "Accidentally escaped delimiter"


basic.f = alt(integer, floating, id, string)

expr.f = basic.f


# def test_string():
#     s = '"Hello"'
#     assert string(s) == Success(Span(s, len(s), len(s)), Node(Span(s, 0, len(s)), Expr.String)), "Success"
    
#     s = "123"
#     assert string(s) == Error(Span(s, 0, None)), "Error"


# ## string
# piece = (pred(lambda c: c not in '\\"{}') + "\\\\" + '\\"' + "\\{" + "\\}").many0().span()
# # interpolant = "{" >> ws >> id << ws << "}"
# # def fix_string_items(x):
# #     first, *rest = x
# #     tokens = [first]
# #     interpolants = []
# #     for (interpolant, piece) in rest:
# #         tokens.append(piece)
# #         interpolants.append(interpolant)
# #     return tokens, interpolants
# # string_items = (piece * (interpolant * piece).many0()).map(fix_string_items).opt()
# string = (
#     (id.opt() * ('"' >> piece << '"'))
#     .spanned()
#     .map(lambda x: Node(x[1], Expr.String, tokens=[x[0][1]]))
# )

# ## array
# array = seq(tag("[") << ws, id.sep(ws >> "," << ws), ws >> "]").map(lambda x: Node(x[0], Expr.Array, children=x[2], tokens=[x[1], x[3]]))

# ## paren
# paren = surround(expr, "(", ")", lambda span, **kwargs: Node(span, Expr.Paren, **kwargs))

# # ## Function literal
# fn = (
#     ((tag("fn") >> ws >> "(" >> (ws >> name).sep(ws * ",") << ws << ")") * (ws >> expr))
#     .spanned()
#     .map(lambda x: Node(x[1], Expr.Fn, children=[x[0][1]], tokens=x[0][0]))
# )

# block = seq("{" << ws, id.many0(), ws >> "}").map(lambda x: Node(x[0], Expr.Block, children=x[2], tokens=[x[1], x[3]]))

# # TODO: match

# basic.f = integer + floating + id + string + array + paren + fn + block

# operators

## postfix
# call = (tag("(") >> ws >> expr << ws << ")").spanned().mark(Call)
# index = (tag("[") >> ws >> expr << ws << "]").spanned().mark(Index)
# field_ = (tag(".") >> ws >> name).spanned().mark(Field)
# await_ = (tag(".") * ws * "await").span().mark(Await)
# chain = (tag(".") * ws * "chain").span().mark(Chain)
# propogate = (ws * "?").span().mark(Propogate)


# def fix(r):
#     f, xs = r
#     for x, m in xs:
#         if isinstance(x, tuple):
#             x, span = x
#             f = m(f.span.span(span), f, x)
#         else:
#             f = m(f.span.span(x), f)
#     return f


# post_exprs = (basic * (call + index + await_ + chain + field_ + propogate).many0()).map(
#     fix
# )

# pow = right(post_exprs, "**", BinOp)

# pre_exprs = recursive(
#     lambda prefix: (((tag("!") + "~" + "-" + ":" + "...") << ws) * prefix)
#     .spanned()
#     .map(lambda x: Prefix(x[1], x[0][0], x[0][1]))
#     + pow
# )

# range_syntax = (
#     seq((pre_exprs << ws).opt(), ".." >> tag("=").opt(), (ws >> pre_exprs).opt())
#     .spanned()
#     .map(
#         lambda x: Range(
#             x[1], x[0][0], x[0][2], "clopen" if x[0][1] is None else "closed"
#         )
#     )
# ) + pre_exprs

# mul = left(range_syntax, tag("*") + "@" + "//" + "/^" + "/" + "%", BinOp)
# add = left(mul, tag("+") + "-", BinOp)
# shift = left(add, tag("<<") + ">>", BinOp)
# bitand = left(shift, tag("&"), BinOp)
# bitxor = left(bitand, tag("^"), BinOp)
# bitor = left(bitxor, tag("|"), BinOp)

# comparator = (
#     tag("in") + "notin" + "isnot" + "is" + "<=" + ">=" + "<" + ">" + "==" + "!="
# )
# comparison = bitor.listfix(comparator, Comparison)

# and_ = left(comparison, "and", BinOp)
# or_ = left(and_, "or", BinOp)

# expr.f = or_

# expr_list.f = expr.sep(ws * "," * ws)

# # Statements

# pattern = name
# let = (
#     (("let" >> ws >> pattern << ws << "=" << ws) * expr)
#     .spanned()
#     .map(lambda x: Let(x[1], *x[0]))
# )
# assign = (
#     ((pattern << ws << "=" << ws) * expr).spanned().map(lambda x: Assign(x[1], *x[0]))
# )

# ## use
# path = Parser()
# path_list = ("(" >> ws >> path.sep(ws >> "," << ws) << ws << ")").map(PathList)
# path_as = (name * (ws >> "as" >> ws >> name).opt()).starmap(PathName)
# path.f = ((name << ws << ".").many0() * (path_as + path_list)).map(lambda x: Path(*x))
# use = ("use" >> ws >> path).spanned().map(lambda x: Use(x[1], x[0]))

# fn_stmt = (
#     seq(
#         "fn" >> ws >> name << ws,
#         "(" >> ws >> name.sep(ws * "," * ws) << ws << ")",
#         ws >> expr,
#     )
#     .spanned()
#     .map(lambda x: FnNamed(x[1], x[0][0], x[0][1], x[0][2]))
# )

# statement = (block + if_stmt + fn_stmt).mark(False) + (let + assign + use + expr).mark(
#     True
# )


# def statements_impl(s0):
#     s = s0
#     final_semi = False
#     stmts = []
#     sep = ws >> tag(";").opt().bool() << ws
#     while (r := statement(s)) is not None:
#         (stmt, requires_semi), s = r
#         stmts.append(stmt)
#         final_semi, s = sep(s)
#         if not final_semi and requires_semi and (r := statement(s)) is not None:
#             raise ValueError(f"Missing semicolon")
#     return Statements(stmts, final_semi), s


# statements.f = statements_impl
