from dataclasses import dataclass, field
from typing import Any


@dataclass
class Input:
    s: str = field(default_factory=input)
    i: int = 0

    @classmethod
    def end(cls, s):
        return cls(s, len(s))

    def __bool__(self):
        """
        >>> bool(Input('xy').advance(1))
        True
        >>> bool(Input('xy').advance(2))
        False
        """
        return self.i < len(self.s)

    def curr(self, n=1):
        """
        >>> Input('asdf').curr()
        'a'
        >>> Input('asdf').curr(2)
        'as'
        """
        return self.s[self.i : self.i + n]

    def advance(self, n=1):
        """
        >>> Input('asdf').advance()
        Input(s='asdf', i=1)
        >>> Input('asdf').advance(2)
        Input(s='asdf', i=2)
        """
        return Input(self.s, self.i + n)

    def span(self, other):
        return Span(self.s, self.i, other.i)


@dataclass
class Span:
    s: str = ""
    i: int = 0
    j: int = 0

    @classmethod
    def all(cls, s):
        return cls(s, 0, len(s))

    def content(self):
        return self.s[self.i : self.j]

    def span(self, other):
        if isinstance(other, Span):
            return Span(self.s, min(self.i, other.i), max(self.j, other.j))
        elif isinstance(other, Input):
            return Span(self.s, min(self.i, other.i), max(self.j, other.i))
        else:
            raise TypeError


@dataclass
class Parser:
    f: Any = None

    def __call__(self, s=None):
        if s is None:
            s = Input()
        elif isinstance(s, str):
            s = Input(s)
        return self.f(s)

    def __add__(self, other):
        """
        >>> p = tag('x') + 'y'
        >>> p('z')
        >>> p('x')
        ('x', Input(s='x', i=1))
        >>> p('y')
        ('y', Input(s='y', i=1))
        """
        other = parser(other)

        @Parser
        def parse(s):
            return self(s) or other(s)

        return parse

    def __radd__(self, other):
        """
        >>> p = 'x' + tag('y')
        >>> p('z')
        >>> p('x')
        ('x', Input(s='x', i=1))
        >>> p('y')
        ('y', Input(s='y', i=1))
        """
        other = parser(other)
        return other + self

    def __mul__(self, other):
        """
        >>> p = tag('x') * 'y'
        >>> p('x')
        >>> p('y')
        >>> p('xy')
        (('x', 'y'), Input(s='xy', i=2))
        """
        other = parser(other)

        @Parser
        def parse(s):
            if r := self(s):
                x, s = r
                if r := other(s):
                    y, s = r
                    return (x, y), s

        return parse

    def __rmul__(self, other):
        """
        >>> p = 'x' * tag('y')
        >>> p('x')
        >>> p('y')
        >>> p('xy')
        (('x', 'y'), Input(s='xy', i=2))
        """
        other = parser(other)
        return other * self

    def __pow__(self, n):
        """
        >>> p = tag('x') ** 5
        >>> p('xxx')
        >>> p('xxxxx')
        (('x', 'x', 'x', 'x', 'x'), Input(s='xxxxx', i=5))
        """
        if isinstance(n, int):
            if n >= 0:
                return seq(*(self for _ in range(n)))
            else:
                raise ValueError
        else:
            raise TypeError

    def __getitem__(self, other):
        """
        >>> p = tag('x')[',']
        >>> p('x')
        ((['x'], []), Input(s='x', i=1))
        >>> p('x,x')
        ((['x', 'x'], [',']), Input(s='x,x', i=3))
        >>> p('x,x,')
        ((['x', 'x'], [',', ',']), Input(s='x,x,', i=4))
        """
        other = parser(other)

        @Parser
        def parse(s):
            xs = []
            ys = []
            while r := self(s):
                x, s = r
                xs.append(x)
                if r := other(s):
                    y, s = r
                    ys.append(y)
                else:
                    break
            return (xs, ys), s

        return parse

    def __lshift__(self, other):
        """
        >>> p = tag('x') << 'y'
        >>> p('xy')
        ('x', Input(s='xy', i=2))
        """
        return (self * other).left()

    def __rlshift__(self, other):
        """
        >>> p = 'x' << tag('y')
        >>> p('xy')
        ('x', Input(s='xy', i=2))
        """
        other = parser(other)
        return other << self

    def __rshift__(self, other):
        """
        >>> p = tag('x') >> 'y'
        >>> p('xy')
        ('y', Input(s='xy', i=2))
        """
        return (self * other).right()

    def __rrshift__(self, other):
        """
        >>> p = 'x' >> tag('y')
        >>> p('xy')
        ('y', Input(s='xy', i=2))
        """
        other = parser(other)
        return other >> self

    def __pos__(self):
        """
        >>> p = +tag('x')
        >>> p('x')
        ('x', Input(s='x', i=1))
        >>> p(' x')
        ('x', Input(s=' x', i=2))
        >>> p('  x')
        ('x', Input(s='  x', i=3))
        >>> p('x ')
        ('x', Input(s='x ', i=1))
        """
        return ws >> self

    def __neg__(self):
        """
        >>> p = -tag('x')
        >>> p(' x')
        >>> p('x')
        ('x', Input(s='x', i=1))
        >>> p('x ')
        ('x', Input(s='x ', i=2))
        >>> p('x  ')
        ('x', Input(s='x  ', i=3))
        """
        return self << ws

    def opt(self):
        """
        >>> p = tag('x').opt()
        >>> p('x')
        ('x', Input(s='x', i=1))
        >>> p('')
        (None, Input(s='', i=0))
        >>> p('y')
        (None, Input(s='y', i=0))
        """

        @Parser
        def parse(s):
            return self(s) or (None, s)

        return parse

    def many0(self):
        """
        >>> p = tag('x').many0()
        >>> p('')
        ([], Input(s='', i=0))
        >>> p('xxxx')
        (['x', 'x', 'x', 'x'], Input(s='xxxx', i=4))
        >>> p('x')
        (['x'], Input(s='x', i=1))
        """

        @Parser
        def parse(s):
            xs = []
            while r := self(s):
                x, s = r
                xs.append(x)
            return xs, s

        return parse

    def many1(self):
        """
        >>> p = tag('x').many1()
        >>> p('')
        >>> p('x')
        (['x'], Input(s='x', i=1))
        >>> p('xxx')
        (['x', 'x', 'x'], Input(s='xxx', i=3))
        """
        return self.many0().pred(len)

    def map(self, f):
        """
        >>> p = (tag('x') * 'y').map(lambda x: x[0])
        >>> p('x')
        >>> p('y')
        >>> p('xy')
        ('x', Input(s='xy', i=2))
        """

        @Parser
        def parse(s):
            if r := self(s):
                x, s = r
                return f(x), s

        return parse

    def starmap(self, f):
        """
        >>> @dataclass
        ... class Two:
        ...     x: Any
        ...     y: Any
        ...
        >>> p = (tag('x') * 'y').starmap(Two)
        >>> p('x')
        >>> p('y')
        >>> p('xy')
        (Two(x='x', y='y'), Input(s='xy', i=2))
        """

        @Parser
        def parse(s):
            if r := self(s):
                x, s = r
                return f(*x), s

        return parse

    def pred(self, p):
        """
        >>> p = (tag('x') + 'y').pred(lambda x: x != 'y')
        >>> p('x')
        ('x', Input(s='x', i=1))
        >>> p('y')
        """

        @Parser
        def parse(s):
            if r := self(s):
                x, s1 = r
                if p(x):
                    return x, s1

        return parse

    def index(self, i):
        """
        >>> p1 = (tag('x') * 'y').index(0)
        >>> p1('x')
        >>> p1('y')
        >>> p1('xy')
        ('x', Input(s='xy', i=2))
        >>> p2 = (tag('x') * 'y').index(1)
        >>> p2('x')
        >>> p2('y')
        >>> p2('xy')
        ('y', Input(s='xy', i=2))
        """
        return self.map(lambda x: x[i])

    def left(self):
        """
        >>> p = tag('x') * 'y'
        >>> p1 = p.left()
        >>> p1('xy')
        ('x', Input(s='xy', i=2))
        """
        return self.index(0)

    def right(self):
        """
        >>> p = tag('x') * 'y'
        >>> p2 = p.right()
        >>> p2('xy')
        ('y', Input(s='xy', i=2))
        """
        return self.index(1)

    def spanned(self):
        """
        >>> p = (tag('x') * 'y').spanned()
        >>> p('xy')
        ((('x', 'y'), Span(s='xy', i=0, j=2)), Input(s='xy', i=2))
        """

        @Parser
        def parse(s):
            if r := self(s):
                x, s1 = r
                span = s.span(s1)
                return (x, span), s1

        return parse

    def span(self):
        """
        >>> p = (tag('x') * 'y').span()
        >>> p('xy')
        (Span(s='xy', i=0, j=2), Input(s='xy', i=2))
        """
        return self.spanned().right()

    def stringed(self):
        """
        >>> p = (tag('x') * 'y').stringed()
        >>> p('xy')
        ((('x', 'y'), 'xy'), Input(s='xy', i=2))
        """

        @Parser
        def parse(s):
            if r := self(s):
                x, s1 = r
                string = s.span(s1).content()
                return (x, string), s1

        return parse

    def string(self):
        """
        >>> p = (tag('x') * 'y').string()
        >>> p('xy')
        ('xy', Input(s='xy', i=2))
        """
        return self.stringed().right()

    def negate(self):
        """
        >>> p = tag('x').negate()
        >>> p('x')
        False
        >>> p('y')
        (None, Input(s='y', i=0))
        """

        @Parser
        def parse(s):
            return (not self(s)) and (None, s)

        return parse

    def sep(self, other):
        """Separate self by other

        Args:
            other (Parser | str): Delimiter

        Returns:
            Parser: parser which separates self by other

        >>> p = tag("x").sep(",")
        >>> s = ""
        >>> p(s)
        ([], Input(s='', i=0))
        >>> s = "x"
        >>> p(s)
        (['x'], Input(s='x', i=1))
        >>> s = "x,x"
        >>> p(s)
        (['x', 'x'], Input(s='x,x', i=3))
        >>> s = "x,x,"
        >>> p(s)
        (['x', 'x'], Input(s='x,x,', i=4))
        """
        other = parser(other)

        @Parser
        def parse(s):
            xs = []
            while (r := self(s)) is not None:
                x, s = r
                xs.append(x)
                if (r := other(s)) is None:
                    break
                _, s = r
            return xs, s

        return parse

    def listfix(self, other, cls=lambda *args: tuple(args)):
        """Separate self by other

        Args:
            other (Parser | str): Delimiter

        Returns:
            Parser: parser which separates self by other, including other in the constructor
        """
        other = ws >> parser(other) << ws

        @Parser
        def parse(s0):
            s = s0
            xs = []
            ops = []
            while (r := self(s)) is not None:
                x, s = r
                xs.append(x)
                if (r := other(s)) is None:
                    break
                op, s = r
                ops.append(op)
            
            if xs and not ops:
                return x, s
            elif xs and ops:
                return cls(s0.span(s), ops, xs), s
            else:
                return

        return parse

    def mark(self, m):
        return self.map(lambda x: (x, m))


def recursive(f):
    p = Parser()
    p.f = f(p)
    return p


def parser(other):
    if isinstance(other, Parser):
        return other
    elif callable(other):
        return Parser(other)
    elif isinstance(other, str):
        return tag(other)
    else:
        raise TypeError


def tag(m):
    """
    >>> tag('...')('')
    >>> tag('...')('...asdf')
    ('...', Input(s='...asdf', i=3))
    """

    @Parser
    def parse(s):
        if s.curr(len(m)) == m:
            return m, s.advance(len(m))

    return parse


def seq(*ps):
    """
    >>> seq('x', 'y', 'z')('xyz')
    (('x', 'y', 'z'), Input(s='xyz', i=3))
    """
    ps = list(map(parser, ps))

    @Parser
    def parse(s):
        xs = []
        for p in ps:
            if (r := p(s)) is not None:
                x, s = r
                xs.append(x)
            else:
                return
        return tuple(xs), s

    return parse


def seqws(*ps):
    """
    >>> p = seqws('x', 'y', 'z')
    >>> p('xyz')
    (('x', 'y', 'z'), Input(s='xyz', i=3))
    >>> p('x y z')
    (('x', 'y', 'z'), Input(s='x y z', i=5))
    >>> p('x y z ')
    (('x', 'y', 'z'), Input(s='x y z ', i=6))
    >>> p('x  y  z  ')
    (('x', 'y', 'z'), Input(s='x  y  z  ', i=9))
    """
    return seq(*(-parser(p) for p in ps))


def seqspanned(*ps):
    """
    >>> p = seqspanned('x', 'y', 'z')
    >>> p('xy')
    >>> p('xyz')
    ((Span(s='xyz', i=0, j=3), 'x', 'y', 'z'), Input(s='xyz', i=3))
    """
    return seqws(*ps).spanned().map(lambda x: (x[1], *x[0]))


@Parser
def one(s):
    """
    >>> one('x')
    ('x', Input(s='x', i=1))
    >>> one(Input('x').advance())
    """
    if s:
        return s.curr(), s.advance()


def pred(p):
    """
    >>> pred(str.isdigit)('xyz')
    >>> pred(str.isdigit)('1234')
    ('1', Input(s='1234', i=1))
    """
    return one.pred(p)


alpha = pred(str.isalpha)
alnum = pred(str.isalnum)
digit = pred(str.isdigit)
lower = pred(str.islower)
upper = pred(str.isupper)
space = pred(str.isspace)

ws = space.many0()


def kw(m):
    return -tag(m).span()


def left(pinner, pop, cls=lambda *args: tuple(args)):
    pinner = parser(pinner)
    pop = parser(pop)
    tail = (ws >> pop << ws) * pinner

    @Parser
    def parse(s0):
        if (r := pinner(s0)) is None:
            return
        left, s = r
        while (r := tail(s)) is not None:
            (op, right), s = r
            left = cls(s0.span(s), op, left, right)
        return left, s

    return parse


def right(pinner, pop, cls=lambda *args: tuple(args)):
    pinner = parser(pinner)
    pop = parser(pop)
    parse = Parser()
    tail = (ws >> pop << ws) * parse

    def parsef(s0):
        if (r := pinner(s0)) is None:
            return
        left, s = r
        if (r := tail(s)) is None:
            return left, s
        (op, right), s = r
        return cls(s0.span(s), op, left, right), s

    parse.f = parsef
    return parse


def pre(pinner, pop, cls=lambda *args: tuple(args)):
    pinner = ws >> pinner
    pop = parser(pop)

    @Parser
    def parse(s0):
        if (r := pop(s0)) is None:
            return pinner(s0)
        op, s = r
        if (r := parse(s)) is None:
            return
        inner, s = r
        return cls(s0.span(s), inner, op), s

    return parse


def post(pinner, pop, cls=lambda *args: tuple(args)):
    pinner = parser(pinner)
    pop = ws >> pop

    @Parser
    def parse(s0):
        if (r := pinner(s0)) is None:
            return
        inner, s = r
        while (r := pop(s)) is not None:
            op, s = r
            inner = cls(s0.span(s), inner, op)
        return inner, s

    return parse


def surround(pinner, pleft, pright, cls=lambda *args: tuple(args)):
    pinner = parser(pinner)
    pleft = pleft << ws
    pright = ws >> pright

    @Parser
    def parse(s0):
        r = seq(pleft, pinner, pright)(s0)
        if r is None:
            return
        (left, inner, right), s = r
        return cls(s0.span(s), inner, left, right), s

    return parse


def test_left():
    p = left("x", "+")
    s = "x+x+x+x"

    e1 = (Span(s, 0, len(s) - 4), "+", "x", "x")
    e2 = (Span(s, 0, len(s) - 2), "+", e1, "x")
    e3 = (Span.all(s), "+", e2, "x")
    assert p(s) == (e3, Input.end(s)), "Successful parse"


def test_right():
    p = right("x", "+")
    s = "x+x+x+x"

    e1 = (Span(s, 4, len(s)), "+", "x", "x")
    e2 = (Span(s, 2, len(s)), "+", "x", e1)
    e3 = (Span.all(s), "+", "x", e2)
    assert p(s) == (e3, Input.end(s)), "Successful parse"


def test_pre():
    p = pre("x", "+")
    s = "+++x"

    e1 = (Span(s, 2, len(s)), "x", "+")
    e2 = (Span(s, 1, len(s)), e1, "+")
    e3 = (Span.all(s), e2, "+")
    assert p(s) == (e3, Input.end(s)), "Successful pa3se"


def test_post():
    p = post("x", "+")
    s = "x+++"

    e1 = (Span(s, 0, 2), "x", "+")
    e2 = (Span(s, 0, 3), e1, "+")
    e3 = (Span.all(s), e2, "+")
    assert p(s) == (e3, Input.end(s)), "Successful pa3se"


def test_surround():
    p = surround("x", "(", ")")
    s = "(x)"
    assert p(s) == ((Span.all(s), "x", "(", ")"), Input.end(s)), "Successful parse"
