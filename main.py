from comb import *

dchash = dataclass(eq=True, frozen=True)

@dchash
class Expr:
  span: Span

@dchash
class Int(Expr): pass

@dchash
class Id(Expr): pass

@dchash
class Paren(Expr):
  kw_lpar: Span
  inner: Expr
  kw_rpar: Span

@dchash
class BinOp(Expr):
  left: Expr
  kw_op: Span
  right: Expr

@dchash
class Pow(BinOp): pass
@dchash
class Mul(BinOp): pass
@dchash
class Div(BinOp): pass
@dchash
class Add(BinOp): pass
@dchash
class Sub(BinOp): pass

run = digit.many1()
integer = (run * ('_' * run).many0()).span().map(Int)
name = (alpha * alnum.many0().optional() * ('_' * alnum.many1()).many0()).span()
ident = name.map(Id)
atom = (ident + integer) << ws

pow = opright([('^', Pow)], atom)
mul = opleft([('*', Mul), ('/', Div)], pow)
add = opleft([('+', Add), ('-', Sub)], mul)

paren = make_parser(lambda paren: seqspanned('(', paren, ')').map_star(Paren) + add)
