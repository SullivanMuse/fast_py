from parse_pattern import *


def test_ignore_pattern():
    s = "_asdf"
    node = IgnorePattern(Span(s, 0, len(s)))
    assert ignore_pattern(s) == Success(Span(s, len(s), len(s)), node), "Success"

    s = ""
    assert ignore_pattern(s) == Error(Span(s, 0, None)), "Error"


def test_id_pattern():
    s = "asdf"
    node = IdPattern(Span(s, 0, len(s)), Span(s, 0, len(s)))
    assert id_pattern(s) == Success(Span(s, len(s), len(s)), node), "Success"

    s = ""
    assert id_pattern(s) == Error(Span(s, 0, None)), "Error"


def test_tag_pattern():
    s = ":asdf"
    node = TagPattern(Span(s, 0, len(s)))
    assert tag_pattern(s) == Success(Span(s, len(s), len(s)), node), "Success"

    s = ""
    assert tag_pattern(s) == Error(Span(s, 0, None)), "Error"


def test_integer_pattern():
    s = "1234"
    node = IntPattern(Span(s, 0, len(s)))
    assert integer_pattern(s) == Success(Span(s, len(s), len(s)), node), "Success"

    s = ""
    assert integer_pattern(s) == Error(Span(s, 0, None)), "Error"


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
