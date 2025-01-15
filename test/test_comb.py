from comb import *


def test_span():
    s = "Hello"
    span = Span(s)
    assert span.str() == s, "String matches input"

    span1, span2 = span.split(3)
    assert span1.str() == "Hel", "a.str() matches first 3"
    assert span2.str() == "lo", "b.str() matches rest"

    span1, span2 = span.split(len(s))
    assert span1.str() == s, "Span all"
    assert span2.str() == "", "Empty final"

    span1, span2 = span.split(len(s) + 1)
    assert span1.str() == s, "Span all"
    assert span2.str() == "", "Empty final"


def test_tag():
    s = "Hello"
    p = tag(s)
    assert p(s) == Success(Span(s, len(s), len(s)), Span(s, stop=len(s))), "Success"

    p = tag("other")
    assert p(s) == Error(Span(s)), "Error"


def test_one():
    s = "Hello"
    p = one
    assert p(s) == Success(Span(s, 1, 5), Span(s, 0, 1)), "Success"
    assert p("") == Error(Span("")), "Error"


def test_pred():
    s = "Hello"
    p = pred("H", lambda s: s.str().isupper())
    assert p(s) == Success(Span(s, 1, 5), Span(s, 0, 1)), "Success"
    assert p("") == Error(Span("")), "Error"


def test_seq():
    s = "Hello"
    p = seq("H", "e")
    assert p(s) == Success(Span(s, 2, 5), [Span(s, 0, 1), Span(s, 1, 2)]), "Success"
    assert p("") == Error(Span("")), "Error"


def test_alt():
    s = "Hello"
    p = alt("e", "H")
    assert p(s) == Success(Span(s, 1, 5), Span(s, 0, 1)), "Success"
    assert p("") == Error(Span("")), "Error"


def test_succeed():
    s = "Hello"
    val = 123
    p = succeed(val)
    assert p(s) == Success(Span(s), val), "Success"


def test_many0():
    s = "xxx"
    p = many0("x")
    assert p(s) == Success(
        Span(s, 3, 3), [Span(s, 0, 1), Span(s, 1, 2), Span(s, 2, 3)]
    ), "Success"
    assert p("") == Success(Span(""), []), "Success"


def test_many1():
    s = "xxx"
    p = many1("x")
    assert p(s) == Success(
        Span(s, 3, 3), [Span(s, 0, 1), Span(s, 1, 2), Span(s, 2, 3)]
    ), "Success"
    assert p("") == Error(Span("")), "Error"


def test_ignore():
    assert ignore(one).ignore, "Ignore"


def test_map():
    s = "Hello"
    p = map(one, lambda span, val: val.str())
    assert p(s) == Success(Span(s, 1, 5), "H"), "Success"
    assert p("") == Error(Span("")), "Error"


def test_right():
    s = "x+x+x"
    p = right("x", "+")
    assert p(s) == Success(
        Span(s, len(s), len(s)),
        (Span(s, 0, 5), Span(s, 0, 1), (Span(s, 2, 5), Span(s, 2, 3), Span(s, 4, 5))),
    ), "Success"
    assert p("") == Error(Span("")), "Error"


# def test_left():
#     s = "x+x+x"
#     p = left("x", "+")
#     assert p(s) == Success(
#         Span(s, len(s), len(s)),
#         (
#             Span(s, 0, 5),
#             (Span(s, 0, 5), Span(s, 0, 1), Span(s, 2, 3), Span(s, 1, 2)),
#             Span(s, 4, 5),
#             Span(s, 3, 4),
#         ),
#     ), "Success"
#     assert p("") == Error(Span("")), "Error"


def test_pre():
    s = "++x"
    p = pre("x", "+")
    assert p(s) == Success(
        Span(s, 3, 3),
        val=(
            Span(s, 0, 3),
            Span(s, 0, 1),
            (Span(s, 1, 3), Span(s, 1, 2), Span(s, 2, 3)),
        ),
    ), "Success"
    assert p("") == Error(Span("")), "Error"


def test_neg():
    s = "y"
    p = neg("x")
    assert p(s) == Success(Span(s), None), "Success"


def test_sep():
    p = sep("x", ",")
    s = "x,x,x"
    assert p(s) == Success(
        Span(s, len(s), len(s)), [Span(s, 0, 1), Span(s, 2, 3), Span(s, 4, 5)]
    )
