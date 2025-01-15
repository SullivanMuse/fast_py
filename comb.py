from dataclasses import dataclass
from typing import Any, Callable, Optional


@dataclass(frozen=True)
class Span:
    string: str
    start: int = 0
    stop: int = None

    def __str__(self):
        return f"{self._range().start}:{self._range().stop} {repr(self.str())}"

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
    reason: Optional[str] = None


@dataclass
class Fail(Result):
    reason: Optional[str] = None


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


def not_implemented(name):
    @Parser
    def parse(s):
        return Fail(s, "Not implemented")

    return parse


@Parser
def one(s):
    s1, s2 = s.split()
    if s1:
        return Success(s2, s1)
    return Error(s)


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


def alt(*ps):
    ps = [Parser.ensure(p) for p in ps]

    @Parser
    def parse(s):
        for p in ps:
            if r := p(s):
                return r
        return Error(s)

    return parse


def succeed(val=None):
    @Parser
    def parse(s):
        return Success(s, val)

    return parse


def opt(*ps):
    return alt(seq(*ps), succeed())


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


def ignore(*ps):
    p = seq(*ps)
    p.ignore = True
    return p


def map(p, f):
    p = Parser.ensure(p)

    @Parser
    def parse(s):
        if r := p(s):
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


def pre(inner, op, cls=lambda span, op, inner: (span, op, inner)):
    return Parser.recursive(lambda p: alt(starmap(seq(op, p), cls), inner))


def neg(*ps):
    p = seq(*ps)

    @Parser
    def parse(s):
        return Error(s) if p(s) else Success(s, None)

    return ignore(parse)


def sep(inner: str | Parser, sep: str | Parser):
    """
    Create parser for the following pattern:
        `inner[sep] = inner (ws sep ws inner)* (ws sep ws)?`

    Args:
        inner (str | Parser): Main parser
        sep (str | Parser): Separator parser

    Returns:
        Parser: Parser for inner[sep]
    """
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


alpha = pred(one, lambda s: s.str().isalpha())
alnum = pred(one, lambda s: s.str().isalpha())
digit = pred(one, lambda s: s.str().isdigit())
