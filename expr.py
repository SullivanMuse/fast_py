from comb import *

dchash = dataclass(eq=True, frozen=True)

@dchash
class Expr:
    span: Span

    def content(self):
        return self.span.content()

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
