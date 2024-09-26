from comb import *
from expr import *
from pprint import pprint

expr = Parser()
expr_list = sep(expr, ",")
statements = Parser()

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
name = seq(neg(keywords), many1(alpha), many0("_", many1(alnum)))
id = map(name, lambda span, _: Node(span, Expr.Id))


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


atom.f = alt(integer, floating, string, id, array, paren)
expr.f = atom

# patterns
pattern = Parser()
integer_pattern = map(dec_run, lambda span, _: Node(span, Pattern.Int))


def test_integer_pattern():
    s = "1234"
    node = Node(Span(s, 0, len(s)), Pattern.Int)
    assert integer_pattern(s) == Success(Span(s, len(s), len(s)), node), "Success"

    s = ""
    assert integer_pattern(s) == Error(Span(s, 0, None)), "Error"


id_pattern = map(name, lambda span, _: Node(span, Pattern.Id))


def test_id_pattern():
    s = "asdf"
    node = Node(Span(s, 0, len(s)), Pattern.Id)
    assert id_pattern(s) == Success(Span(s, len(s), len(s)), node), "Success"

    s = ""
    assert id_pattern(s) == Error(Span(s, 0, None)), "Error"


gather = starmap(
    seq("...", opt(pattern)),
    lambda span, ellipsis, inner: Node(
        span,
        Pattern.Gather,
        children=[] if inner is None else [inner],
        tokens=[ellipsis],
    ),
)


def test_gather():
    s = "...x"
    assert gather(s) == Success(
        Span(s, len(s), len(s)),
        Node(
            Span(s, 0, len(s)),
            Pattern.Gather,
            children=[Node(Span(s, 3, 4), Pattern.Id)],
            tokens=[Span(s, 0, 3)],
        ),
    )


pattern.f = alt(integer_pattern, id_pattern)
