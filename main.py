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
atom = ident + integer

pow = opright([('^', Pow)], atom)
mul = opleft([('*', Mul), ('/', Div)], pow)
add = opleft([('+', Add), ('-', Sub)], mul)

paren = make_parser(lambda paren: seqspanned('(', paren, ')').map_star(Paren) + add)

def test_integer():
  s = "1234"
  assert integer(s) == (Int(Span.all(s)), Input(s, len(s))), "Successful parse"
  
  s = "123_456"
  assert integer(s) == (Int(Span.all(s)), Input(s, len(s))), "Successful parse"
  
  s = "_123"
  assert integer(s) is None, "Unsuccesful parse"
  
  s = ""
  assert integer(s) is None, "Unsuccesful parse"

def test_ident():
  s = "asdf"
  assert ident(s) == (Id(Span.all(s)), Input(s, len(s))), "Successful parse"
  
  s = "Hello123"
  assert ident(s) == (Id(Span.all(s)), Input(s, len(s))), "Successful parse"
  
  s = "1234asdf"
  assert ident(s) is None, "Unsuccessful parse"
