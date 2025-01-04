# Project
from comb import *
from tree import *

expr = Parser()
expr_list = sep(expr, ",")

# atom
atom = Parser()

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


## float
fraction = map(seq(".", dec_run), lambda span, _: span)
exponent = map(seq("e", opt("-"), dec_run), lambda span, _: span)
s = seq(dec_run, opt(fraction), opt(exponent))
floating = map(
    pred(s, lambda x: not (x[1] is None or x[2] is None)),
    lambda span, _: Node(span, Expr.Float),
)


def test_float():
    s = "123.456e789"
    node = Node(Span(s, 0, len(s)), Expr.Float)
    assert floating(s) == Success(Span(s, len(s), len(s)), node), "Success"

    s = "123"
    assert floating(s) == Error(Span(s, 0, None)), "Error"


## id
keywords = alt(
    "if",
    "else",
    "use",
    "fn",
    "await",
    "chain",
    "loop",
    "while",
    "for",
    "repeat",
    "break",
    "continue",
    "return",
    "and",
    "or",
    "in",
    "notin",
    "isnot",
    "is",
)
name = map(
    seq(neg(keywords), many1(alpha), many0("_", many1(alnum))), lambda span, _: span
)
id = map(name, lambda span, _: Node(span, Expr.Id))
tag_expr = map(seq(ignore(":"), name), lambda span, r: Node(span, Expr.Tag, tokens=[r]))


def test_tag_expr():
    s = ":asdf"
    node = Node(Span(s, 0, len(s)), Expr.Tag, tokens=[Span(s, 1, len(s))])
    assert tag_expr(s) == Success(Span(s, len(s), len(s)), node), "Success"

    s = ""
    assert tag_expr(s) == Error(Span(s, 0, None)), "Error"


def test_id():
    s = "asdf"
    node = Node(Span(s, 0, len(s)), Expr.Id)
    assert id(s) == Success(Span(s, len(s), len(s)), node), "Success"

    s = "123"
    assert id(s) == Error(Span(s, 0, None)), "Error"


## string
escape = seq("\\", alt("\\", '"', "{", "}"))
forbidden = set(r"\"{}")
regular = pred(one, lambda s: s.str() not in forbidden)
interpolant = map(seq(ignore("{"), expr, ignore("}")), lambda _, item: item)
piece = map(many0(alt(regular, escape)), lambda span, _: span)
string_impl = seq(ignore('"'), many0(piece, interpolant), piece, ignore('"'))
string = starmap(
    string_impl,
    lambda span, pis, piece: Node(
        span,
        Expr.String,
        children=[i for _, i in pis],
        tokens=[*(p for p, _ in pis), piece],
    ),
)


def test_string():
    s = '"asdf\\""'
    assert len(s) == 8
    assert string(s) == Success(
        Span(s, len(s), len(s)),
        Node(Span(s, 0, len(s)), Expr.String, children=[], tokens=[Span(s, 1, 7)]),
    )

    s = '"asdf\\"'
    assert len(s) == 7
    assert string(s) == Error(Span(s)), "Accidentally escaped delimiter"


## array
array = starmap(
    seq("[", ignore(ws), expr_list, ignore(ws), "]"),
    lambda span, lsq, exprs, rsq: Node(
        span, Expr.Array, children=exprs, tokens=[lsq, rsq]
    ),
)


def test_array():
    s = "[x, y, z]"
    assert array(s) == Success(
        Span(s, len(s), len(s)),
        Node(
            Span(s, 0, len(s)),
            Expr.Array,
            children=[
                Node(Span(s, 1, 2), Expr.Id),
                Node(Span(s, 4, 5), Expr.Id),
                Node(Span(s, 7, 8), Expr.Id),
            ],
            tokens=[Span(s, 0, 1), Span(s, len(s) - 1, len(s))],
        ),
    )


## paren
paren = starmap(
    seq("(", expr, ")"),
    lambda span, lpar, expr, rpar: Node(
        span, Expr.Paren, children=[expr], tokens=[lpar, rpar]
    ),
)


def test_paren():
    s = "(x)"
    assert paren(s) == Success(
        Span(s, len(s), len(s)),
        Node(
            Span(s, 0, len(s)),
            Expr.Paren,
            children=[Node(Span(s, 1, 2), Expr.Id)],
            tokens=[Span(s, 0, 1), Span(s, 2, 3)],
        ),
    )


spread = map(
    seq("..", ignore(ws), expr),
    lambda span, rs: Node(span, Expr.Spread, children=[rs[1]], tokens=[rs[0]]),
)


def test_spread():
    s = "..r"
    assert spread(s) == Success(
        Span(s, len(s), len(s)),
        Node(
            Span(s, 0, len(s)),
            Expr.Spread,
            children=[Node(Span(s, 2, 3), Expr.Id)],
            tokens=[Span(s, 0, 2)],
        ),
    )


atom.f = alt(integer, floating, string, id, tag_expr, array, paren)
expr.f = atom
