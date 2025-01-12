from comb import *
from parse_expr import name, dec_run, expr
from tree import *

pattern = Parser()

ignore_pattern = map(seq("_", name), lambda span, _: IgnorePattern(span))


def test_ignore_pattern():
    s = "_asdf"
    node = IgnorePattern(Span(s, 0, len(s)))
    assert ignore_pattern(s) == Success(Span(s, len(s), len(s)), node), "Success"

    s = ""
    assert ignore_pattern(s) == Error(Span(s, 0, None)), "Error"


id_pattern = map(name, lambda span, _: IdPattern(span, span))


def test_id_pattern():
    s = "asdf"
    node = IdPattern(Span(s, 0, len(s)), Span(s, 0, len(s)))
    assert id_pattern(s) == Success(Span(s, len(s), len(s)), node), "Success"

    s = ""
    assert id_pattern(s) == Error(Span(s, 0, None)), "Error"


tag_pattern = map(seq(ignore(":"), name), lambda span, _: TagPattern(span))


def test_tag_pattern():
    s = ":asdf"
    node = TagPattern(Span(s, 0, len(s)))
    assert tag_pattern(s) == Success(Span(s, len(s), len(s)), node), "Success"

    s = ""
    assert tag_pattern(s) == Error(Span(s, 0, None)), "Error"


integer_pattern = map(dec_run, lambda span, _: IntPattern(span))


def test_integer_pattern():
    s = "1234"
    node = IntPattern(Span(s, 0, len(s)))
    assert integer_pattern(s) == Success(Span(s, len(s), len(s)), node), "Success"

    s = ""
    assert integer_pattern(s) == Error(Span(s, 0, None)), "Error"


float_pattern = not_implemented("float_pattern")
string_pattern = not_implemented("string_pattern")

gather_pattern = starmap(
    seq("..", opt(pattern)),
    GatherPattern,
)


def test_gather():
    s = "..x"
    assert gather_pattern(s) == Success(
        Span(s, len(s), len(s)),
        GatherPattern(
            span=Span(s, 0, len(s)),
            ellipsis=Span(s, 0, 2),
            inner=IdPattern(Span(s, 2, 3), Span(s, 2, 3)),
        ),
    )


@Parser
def array_pattern_items(s0):
    sep = map(seq(ignore(ws), ",", ignore(ws)), lambda _, sep: sep)
    s = s0

    items = []
    commas = []

    item = alt(pattern, gather_pattern)
    while r := item(s):
        s = r.span
        items.append(r.val)
        if not (r := sep(s)):
            break
        s = r.span
        commas.append(r.val)

    gather_count = sum(1 for item in items if isinstance(item, GatherPattern))
    if gather_count not in (0, 1):
        return Fail(s0.span(s), "Too many gather patterns")

    gather_index = 0
    for item in items:
        if isinstance(item, GatherPattern):
            break
        gather_index += 1
    else:
        gather_index = None

    return Success(s, (items, commas))


array_pattern = starmap(
    seq("[", ignore(ws), array_pattern_items, ignore(ws), "]"),
    lambda span, lsq, items, rsq: ArrayPattern(
        span,
        items[0],
        lsq,
        items[1],
        rsq,
    ),
)


def test_array_pattern():
    s = "[1, 2, ..r, 4]"
    assert array_pattern(s) == Success(
        Span(s, len(s), len(s)),
        ArrayPattern(
            Span(s, 0, len(s)),
            items=[
                IntPattern(Span(s, 1, 2)),
                IntPattern(Span(s, 4, 5)),
                GatherPattern(
                    span=Span(s, 7, 10),
                    ellipsis=Span(s, 7, 9),
                    inner=IdPattern(Span(s, 9, 10), Span(s, 9, 10)),
                ),
                IntPattern(Span(s, 12, 13)),
            ],
            lsq=Span(s, 0, 1),
            commas=[
                Span(s, 2, 3),
                Span(s, 5, 6),
                Span(s, 10, 11),
            ],
            rsq=Span(s, 13, 14),
        ),
    )

    s = "[]"
    assert array_pattern(s) == Success(
        Span(s, len(s), len(s)),
        ArrayPattern(
            span=Span(s, 0, len(s)),
            items=[],
            lsq=Span(s, 0, 1),
            commas=[],
            rsq=Span(s, 1, 2),
        ),
    )

    s = "[..r]"
    assert array_pattern(s) == Success(
        Span(s, len(s), len(s)),
        ArrayPattern(
            span=Span(s, 0, len(s)),
            items=[
                GatherPattern(
                    span=Span(s, 1, len(s) - 1),
                    ellipsis=Span(s, 1, 3),
                    inner=IdPattern(
                        Span(s, len(s) - 2, len(s) - 1), Span(s, len(s) - 2, len(s) - 1)
                    ),
                )
            ],
            lsq=Span(s, 0, 1),
            commas=[],
            rsq=Span(s, len(s) - 1, len(s)),
        ),
    )

    s = "[a, ..r]"
    assert array_pattern(s) == Success(
        Span(s, len(s), len(s)),
        ArrayPattern(
            span=Span(s, 0, len(s)),
            items=[
                IdPattern(Span(s, 1, 2), Span(s, 1, 2)),
                GatherPattern(
                    span=Span(s, len(s) - 4, len(s) - 1),
                    ellipsis=Span(s, len(s) - 4, len(s) - 2),
                    inner=IdPattern(
                        Span(s, len(s) - 2, len(s) - 1), Span(s, len(s) - 2, len(s) - 1)
                    ),
                ),
            ],
            lsq=Span(s, 0, 1),
            commas=[Span(s, 2, 3)],
            rsq=Span(s, len(s) - 1, len(s)),
        ),
    )

    s = "[..r, a]"
    assert array_pattern(s) == Success(
        Span(s, len(s), len(s)),
        ArrayPattern(
            span=Span(s, 0, len(s)),
            items=[
                GatherPattern(
                    span=Span(s, 1, 4),
                    ellipsis=Span(s, 1, 3),
                    inner=IdPattern(Span(s, 3, 4), Span(s, 3, 4)),
                ),
                IdPattern(Span(s, 6, 7), Span(s, 6, 7)),
            ],
            lsq=Span(s, 0, 1),
            commas=[Span(s, 4, 5)],
            rsq=Span(s, len(s) - 1, len(s)),
        ),
    )

    s = "[a]"
    assert array_pattern(s) == Success(
        Span(s, len(s), len(s)),
        ArrayPattern(
            span=Span(s, 0, len(s)),
            items=[
                IdPattern(Span(s, 1, 2), Span(s, 1, 2)),
            ],
            lsq=Span(s, 0, 1),
            commas=[],
            rsq=Span(s, len(s) - 1, len(s)),
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
    gather_pattern,
)
