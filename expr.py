from comb import *

dchash = dataclass(eq=True, frozen=True)

@dchash
class Expr:
    span: Span

    def content(self):
        return self.span.content()

@dchash
class Id(Expr):
    pass

@dchash
class Fn(Expr):
    keys: tuple[Span]
    kw_arrow: Span
    body: Expr

@dchash
class Integer(Expr):
    pass

@dchash
class IntegerType(Expr):
    pass

@dchash
class TypeType(Expr):
    pass

@dchash
class Ann(Expr):
    left: Expr
    kw_colon: Span
    right: Expr
