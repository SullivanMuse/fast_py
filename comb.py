from dataclasses import dataclass, field
from typing import Any, Callable, Optional


@dataclass(frozen=True)
class Span:
    string: str
    start: int = 0
    stop: int = None

    def str(self):
        return self.string[self._slice()]

    def _slice(self):
        return slice(self.start, self.stop)

    def _range(self):
        return range(*self._slice().indices(len(self.string)))

    def __len__(self):
        return len(self._range())

    def __bool__(self):
        return len(self) != 0

    def span(self, other):
        assert self.string is other.string, "Strings must be identical"
        start1 = self._range().start
        start2 = other._range().start
        start = min(start1, start2)
        stop = max(start1, start2)
        return Span(self.string, start, stop)

    def split(self, n=1):
        r = self._range()
        start = r.start
        stop = r.stop
        n = min(start + n, stop)
        return Span(self.string, start, n), Span(self.string, n, stop)


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


@dataclass
class Result:
    span: Span

    def __bool__(self):
        return False


@dataclass
class Success(Result):
    val: Any

    def __bool__(self):
        return True

    def set_val(self, val):
        return Success(self.span, val)


@dataclass
class Error(Result):
    pass


@dataclass
class Fail(Result):
    pass


@dataclass
class Parser:
    f: Optional[Callable[[Span], Result]] = None
    ignore: bool = False

    @classmethod
    def recursive(cls, f):
        out = cls()
        out.f = f(out)
        return out

    @classmethod
    def ensure(cls, p):
        if isinstance(p, str):
            p = tag(p)
        return p

    def __call__(self, s: str | Span):
        if isinstance(s, str):
            s = Span(s)
        if not isinstance(s, Span):
            raise TypeError
        return self.f(s)


def tag(m):
    @Parser
    def parse(s):
        s1, s2 = s.split(len(m))
        if s1.str() == m:
            return Success(s2, s1)
        return Error(s)

    return parse


def test_tag():
    s = "Hello"
    p = tag(s)
    assert p(s) == Success(Span(s, len(s), len(s)), Span(s, stop=len(s))), "Success"

    p = tag("other")
    assert p(s) == Error(Span(s)), "Error"


@Parser
def one(s):
    s1, s2 = s.split()
    if s1:
        return Success(s2, s1)
    return Error(s)


def test_one():
    s = "Hello"
    p = one
    assert p(s) == Success(Span(s, 1, 5), Span(s, 0, 1)), "Success"
    assert p("") == Error(Span("")), "Error"


def pred(p, f):
    p = Parser.ensure(p)

    @Parser
    def parse(s):
        r = p(s)
        if r:
            if f(r.val):
                return r
            return Error(s)
        return r

    return parse


def test_pred():
    s = "Hello"
    p = pred("H", lambda s: s.str().isupper())
    assert p(s) == Success(Span(s, 1, 5), Span(s, 0, 1)), "Success"
    assert p("") == Error(Span("")), "Error"


def seq(*ps):
    ps = [Parser.ensure(p) for p in ps]
    if len(ps) == 1:
        return ps[0]

    @Parser
    def parse(s0):
        s = s0
        vals = []
        for p in ps:
            if r := p(s):
                if not p.ignore:
                    vals.append(r.val)
                s = r.span
            else:
                return Error(s)
        return Success(s, vals[0] if len(vals) == 1 else vals)

    return parse


def test_seq():
    s = "Hello"
    p = seq("H", "e")
    assert p(s) == Success(Span(s, 2, 5), [Span(s, 0, 1), Span(s, 1, 2)]), "Success"
    assert p("") == Error(Span("")), "Error"


def alt(*ps):
    ps = [Parser.ensure(p) for p in ps]

    @Parser
    def parse(s):
        for p in ps:
            if r := p(s):
                return r
        return Error(s)

    return parse


def test_alt():
    s = "Hello"
    p = alt("e", "H")
    assert p(s) == Success(Span(s, 1, 5), Span(s, 0, 1)), "Success"
    assert p("") == Error(Span("")), "Error"


def succeed(val=None):
    @Parser
    def parse(s):
        return Success(s, val)

    return parse


def test_succeed():
    s = "Hello"
    val = 123
    p = succeed(val)
    assert p(s) == Success(Span(s), val), "Success"


def opt(*ps):
    return alt(seq(*ps), succeed())


def test_opt():
    s = "Hello"
    p = opt("H")
    assert p(s) == Success(Span(s, 1, 5), Span(s, 0, 1)), "Success"
    assert p("") == Success(Span(""), None), "Success"


def many0(*ps):
    p = seq(*ps)

    @Parser
    def parse(s0):
        s = s0
        vals = []
        while r := p(s):
            s = r.span
            vals.append(r.val)
        return Success(s, vals)

    return parse


def test_many0():
    s = "xxx"
    p = many0("x")
    assert p(s) == Success(
        Span(s, 3, 3), [Span(s, 0, 1), Span(s, 1, 2), Span(s, 2, 3)]
    ), "Success"
    assert p("") == Success(Span(""), []), "Success"


def many1(*ps):
    p = seq(*ps)

    @Parser
    def parse(s0):
        s = s0
        if r := p(s):
            s = r.span
            vals = [r.val]
            while r := p(s):
                s = r.span
                vals.append(r.val)
            return Success(s, vals)
        return Error(s)

    return parse


def test_many1():
    s = "xxx"
    p = many1("x")
    assert p(s) == Success(
        Span(s, 3, 3), [Span(s, 0, 1), Span(s, 1, 2), Span(s, 2, 3)]
    ), "Success"
    assert p("") == Error(Span("")), "Error"


def ignore(*ps):
    p = seq(*ps)
    p.ignore = True
    return p


def test_ignore():
    assert ignore(one).ignore, "Ignore"


def map(p, f):
    p = Parser.ensure(p)

    @Parser
    def parse(s):
        if r := p(s):
            print(f"{s = }")
            print(f"{r.span = }")
            span = s.span(r.span)
            return Success(r.span, f(span, r.val))
        return Error(s)

    return parse


def starmap(p, f):
    p = Parser.ensure(p)

    @Parser
    def parse(s):
        if r := p(s):
            span = s.span(r.span)
            return Success(r.span, f(span, *r.val))
        return Error(s)

    return parse


def test_map():
    s = "Hello"
    p = map(one, lambda span, val: val.str())
    assert p(s) == Success(Span(s, 1, 5), "H"), "Success"
    assert p("") == Error(Span("")), "Error"


space = pred(one, lambda s: s.str().isspace())
ws = many0(space)


def recurse(f):
    p = Parser()
    p.f = f(p)
    return p


def right(inner, op, cls=lambda *args: tuple(args)):
    inner = Parser.ensure(inner)
    op = Parser.ensure(op)
    return recurse(
        lambda p: starmap(
            seq(inner, opt(ignore(ws, op, ws), p)),
            lambda span, left, right: cls(span, left, right) if right else left,
        )
    )


def test_right():
    s = "x+x+x"
    p = right("x", "+")
    assert p(s) == Success(
        Span(s, len(s), len(s)),
        (Span(s, 0, 5), Span(s, 0, 1), (Span(s, 2, 5), Span(s, 2, 3), Span(s, 4, 5))),
    ), "Success"
    assert p("") == Error(Span("")), "Error"


def left(inner, op, cls=lambda span, left, right, op: (span, left, right, op)):
    inner = Parser.ensure(inner)
    op = Parser.ensure(op)
    tail = seq(ignore(ws), op, ignore(ws), inner)

    @Parser
    def parse(s):
        if r := inner(s):
            left = r.val
            while r := tail(r.span):
                op, right = r.val
                span = s.span(r.span)
                left = cls(span, left, right, op)
            return Success(r.span, left)
        return Error(s)

    return parse


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


def pre(inner, op, cls=lambda span, op, inner: (span, op, inner)):
    return Parser.recursive(lambda p: alt(starmap(seq(op, p), cls), inner))


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


def neg(*ps):
    p = seq(*ps)

    @Parser
    def parse(s):
        return Error(s) if p(s) else Success(s, None)

    return ignore(parse)


def test_neg():
    s = "y"
    p = neg("x")
    assert p(s) == Success(Span(s), None), "Success"


def sep(inner, sep):
    inner = Parser.ensure(inner)
    sep = Parser.ensure(sep)
    sep = map(seq(ignore(ws), sep, ignore(ws)), lambda _, sep: sep)
    @Parser
    def parse(s0):
        s = s0
        vals = []
        while r := inner(s):
            vals.append(r.val)
            s = r.span
            if r := sep(s):
                s = r.span
            else:
                break
        return Success(s, vals)
    return parse


def test_sep():
    p = sep("x", ",")
    s = "x,x,x"
    assert p(s) == Success(Span(s, len(s), len(s)), [Span(s, 0, 1), Span(s, 2, 3), Span(s, 4, 5)])


alpha = pred(one, lambda s: s.str().isalpha())
alnum = pred(one, lambda s: s.str().isalpha())
digit = pred(one, lambda s: s.str().isdigit())
