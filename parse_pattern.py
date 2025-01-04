# project
from comb import *
from tree import *
from parse_expr import name, dec_run

pattern = Parser()

ignore_pattern = map(seq("_", name), lambda span, _: SyntaxNode(span, PatternTy.Ignore))


def test_ignore_pattern():
    s = "_asdf"
    node = SyntaxNode(Span(s, 0, len(s)), PatternTy.Ignore)
    assert ignore_pattern(s) == Success(Span(s, len(s), len(s)), node), "Success"

    s = ""
    assert ignore_pattern(s) == Error(Span(s, 0, None)), "Error"


id_pattern = map(name, lambda span, _: SyntaxNode(span, PatternTy.Id))


def test_id_pattern():
    s = "asdf"
    node = SyntaxNode(Span(s, 0, len(s)), PatternTy.Id)
    assert id_pattern(s) == Success(Span(s, len(s), len(s)), node), "Success"

    s = ""
    assert id_pattern(s) == Error(Span(s, 0, None)), "Error"


tag_pattern = map(
    seq(ignore(":"), name), lambda span, r: SyntaxNode(span, PatternTy.Tag, tokens=[r])
)


def test_tag_pattern():
    s = ":asdf"
    node = SyntaxNode(Span(s, 0, len(s)), PatternTy.Tag, tokens=[Span(s, 1, len(s))])
    assert tag_pattern(s) == Success(Span(s, len(s), len(s)), node), "Success"

    s = ""
    assert tag_pattern(s) == Error(Span(s, 0, None)), "Error"


integer_pattern = map(dec_run, lambda span, _: SyntaxNode(span, PatternTy.Int))


def test_integer_pattern():
    s = "1234"
    node = SyntaxNode(Span(s, 0, len(s)), PatternTy.Int)
    assert integer_pattern(s) == Success(Span(s, len(s), len(s)), node), "Success"

    s = ""
    assert integer_pattern(s) == Error(Span(s, 0, None)), "Error"


float_pattern = not_implemented("float_pattern")
string_pattern = not_implemented("string_pattern")
range_pattern = not_implemented("range_pattern")

gather_pattern = starmap(
    seq("..", opt(pattern)),
    lambda span, ellipsis, inner: SyntaxNode(
        span,
        PatternTy.Gather,
        children=[] if inner is None else [inner],
        tokens=[ellipsis],
    ),
)


def test_gather():
    s = "..x"
    assert gather_pattern(s) == Success(
        Span(s, len(s), len(s)),
        SyntaxNode(
            Span(s, 0, len(s)),
            PatternTy.Gather,
            children=[SyntaxNode(Span(s, 2, 3), PatternTy.Id)],
            tokens=[Span(s, 0, 2)],
        ),
    )


@Parser
def array_pattern_items(s0):
    sep = map(seq(ignore(ws), ",", ignore(ws)), lambda _, sep: sep)
    s = s0

    items = []
    tokens = []

    item = alt(pattern, gather_pattern)
    while r := item(s):
        s = r.span
        items.append(r.val)
        if not (r := sep(s)):
            break
        s = r.span
        tokens.append(r.val)

    gather_count = sum(1 for it in items if it.ty == PatternTy.Gather)
    if gather_count not in (0, 1):
        return Fail(s0.span(s), "Too many gather patterns")

    gather_index = 0
    for item in items:
        if item.ty == PatternTy.Gather:
            break
        gather_index += 1
    else:
        gather_index = None

    return Success(s, (items, tokens))


array_pattern = starmap(
    seq("[", ignore(ws), array_pattern_items, ignore(ws), "]"),
    lambda span, lsq, items, rsq: SyntaxNode(
        span, PatternTy.Array, children=items[0], tokens=[lsq, *items[1], rsq]
    ),
)


def test_array_pattern():
    s = "[1, 2, ..r, 4]"
    assert array_pattern(s) == Success(
        Span(s, len(s), len(s)),
        SyntaxNode(
            Span(s, 0, len(s)),
            PatternTy.Array,
            children=[
                SyntaxNode(Span(s, 1, 2), PatternTy.Int),
                SyntaxNode(Span(s, 4, 5), PatternTy.Int),
                SyntaxNode(
                    Span(s, 7, 10),
                    PatternTy.Gather,
                    children=[SyntaxNode(Span(s, 9, 10), PatternTy.Id)],
                    tokens=[Span(s, 7, 9)],
                ),
                SyntaxNode(Span(s, 12, 13), PatternTy.Int),
            ],
            tokens=[
                Span(s, 0, 1),
                Span(s, 2, 3),
                Span(s, 5, 6),
                Span(s, 10, 11),
                Span(s, 13, 14),
            ],
        ),
    )

    s = "[]"
    assert array_pattern(s) == Success(
        Span(s, len(s), len(s)),
        SyntaxNode(
            Span(s, 0, len(s)),
            PatternTy.Array,
            children=[],
            tokens=[Span(s, 0, 1), Span(s, 1, 2)],
        ),
    )

    s = "[..r]"
    assert array_pattern(s) == Success(
        Span(s, len(s), len(s)),
        SyntaxNode(
            Span(s, 0, len(s)),
            PatternTy.Array,
            children=[
                SyntaxNode(
                    Span(s, 1, len(s) - 1),
                    PatternTy.Gather,
                    children=[
                        SyntaxNode(Span(s, len(s) - 2, len(s) - 1), PatternTy.Id)
                    ],
                    tokens=[Span(s, 1, 3)],
                )
            ],
            tokens=[Span(s, 0, 1), Span(s, len(s) - 1, len(s))],
        ),
    )

    s = "[a, ..r]"
    assert array_pattern(s) == Success(
        Span(s, len(s), len(s)),
        SyntaxNode(
            Span(s, 0, len(s)),
            PatternTy.Array,
            children=[
                SyntaxNode(Span(s, 1, 2), PatternTy.Id),
                SyntaxNode(
                    Span(s, len(s) - 4, len(s) - 1),
                    PatternTy.Gather,
                    children=[
                        SyntaxNode(Span(s, len(s) - 2, len(s) - 1), PatternTy.Id),
                    ],
                    tokens=[Span(s, len(s) - 4, len(s) - 2)],
                ),
            ],
            tokens=[Span(s, 0, 1), Span(s, 2, 3), Span(s, len(s) - 1, len(s))],
        ),
    )

    s = "[..r, a]"
    assert array_pattern(s) == Success(
        Span(s, len(s), len(s)),
        SyntaxNode(
            Span(s, 0, len(s)),
            PatternTy.Array,
            children=[
                SyntaxNode(
                    Span(s, 1, 4),
                    PatternTy.Gather,
                    children=[
                        SyntaxNode(Span(s, 3, 4), PatternTy.Id),
                    ],
                    tokens=[Span(s, 1, 3)],
                ),
                SyntaxNode(Span(s, 6, 7), PatternTy.Id),
            ],
            tokens=[Span(s, 0, 1), Span(s, 4, 5), Span(s, len(s) - 1, len(s))],
        ),
    )

    s = "[a]"
    assert array_pattern(s) == Success(
        Span(s, len(s), len(s)),
        SyntaxNode(
            Span(s, 0, len(s)),
            PatternTy.Array,
            children=[
                SyntaxNode(Span(s, 1, 2), PatternTy.Id),
            ],
            tokens=[Span(s, 0, 1), Span(s, len(s) - 1, len(s))],
        ),
    )


pattern.f = alt(
    ignore_pattern,
    id_pattern,
    tag_pattern,
    integer_pattern,
    float_pattern,
    string_pattern,
    array_pattern,
    range_pattern,
    gather_pattern,
)
