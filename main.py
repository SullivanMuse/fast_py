from comb import *
import expr
import value

# Parse
ex = Parser()
key = (alpha * ('_' + alnum).many0()).span()
id = key.map(expr.Id)
integer = (digit.many1() * ('_' * digit.many1()).many0() * tag('_').negate()).span().map(expr.Integer)
integer_type = kw('int').span().map(expr.IntegerType)
type_type = kw('type').span().map(expr.TypeType)
fn = (+seqspanned((-key).many1(), kw('->'), ex)).map_star(expr.Fn)
ex_not_ann = integer + integer_type + type_type + fn + id

ann = (+seqspanned(-ex_not_ann, kw(':'), +-ex)).map_star(expr.Ann)
ex.f = ann + ex_not_ann

def parse(s):
    r, _ = ex(s)
    return r

@dataclass
class Interp:
    values: dict[str, value.Value] = field(default_factory=dict)

    def eval(self, ex: expr.Expr) -> value.Value:
        '''
        >>> eval(parse('1234'))
        Integer(value=1234)
        >>> eval(parse('1234: 1234'))
        Integer(value=1234)
        >>> eval(parse('int'))
        IntegerType()
        >>> eval(parse('type'))
        TypeType()
        '''
        if isinstance(ex, expr.Integer):
            return value.Integer(int(ex.content()))
        elif isinstance(ex, expr.Ann):
            return eval(ex.left)
        elif isinstance(ex, expr.IntegerType):
            return value.IntegerType()
        elif isinstance(ex, expr.TypeType):
            return value.TypeType()
        elif isinstance(ex, expr.Fn):
            pass

@dataclass
class Environment:
    types: dict[str, value.Value]

    def __getitem__(self, key):
        return self.types[key]
    
    def check1(self, ex: expr.Expr) -> bool:
        pass

def check(ex: expr.Expr) -> bool:
    '''
    >>> check(parse('1234: int'))
    True
    >>> check(parse('int: type'))
    True
    '''
    if isinstance(ex, expr.Ann):
        return infer(ex.left) == eval(ex.right)
    else:
        return True

def infer(ex: expr.Expr) -> value.Value:
    if isinstance(ex, expr.Integer):
        return value.IntegerType()
    elif isinstance(ex, (expr.IntegerType, expr.TypeType)):
        return value.TypeType()
    elif isinstance(ex, expr.Ann):
        return infer(ex.left)
