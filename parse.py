from comb import *
from expr import *

expr = Parser()

# atom
atom = Parser()

## integer
dec_digits = digit.many1()
dec_run = (dec_digits * ("_" * dec_digits).many0()).span()
integer = dec_run.map(Integer)

## float
fraction = ("." * dec_run).span()
exponent = ("e" * tag("-").opt() * dec_run).span()
floating = (
    seq(dec_run, fraction.opt(), exponent.opt())
    .pred(lambda x: not (x[1] is None and x[2] is None))
    .span()
    .map(Float)
)

## id
name = (alpha * ("_" + alnum).many0()).span()
id = name.map(Id)

## string
character = pred(lambda c: c not in '\\"{}').span()
escape = (tag("\\\\") + '\\"' + "\\{" + "\\}").span()
interpolant = "{" >> ws >> expr << ws << "}"
string_item = character + escape + interpolant
string = (
    (id.opt() * ('"' >> string_item.many0() << '"'))
    .spanned()
    .map(lambda x: String(x[1], x[0][0], x[0][1]))
)

## array
array = surround(expr.opt(), "[", "]", Array)

## paren
paren = surround(expr, "(", ")",  Paren)

atom.f = integer + floating + id + string + array + paren

# operators

## postfix
call = (tag("(") >> ws >> expr << ws << ")").spanned().mark(Call)
index = (tag("[") >> ws >> expr << ws << "]").spanned().mark(Index)
field_ = (tag(".") >> ws >> name).spanned().mark(Field)
await_ = (tag(".") * ws * "await").span().mark(Await)
chain = (tag(".") * ws * "chain").span().mark(Chain)
propogate = (ws * "?").span().mark(Propogate)


def fix(r):
    f, xs = r
    for x, m in xs:
        if isinstance(x, tuple):
            x, span = x
            f = m(f.span.span(span), f, x)
        else:
            f = m(f.span.span(x), f)
    return f


post_exprs = (atom * (call + index + await_ + chain + field_ + propogate).many0()).map(fix)

range_syntax = (
    seq((atom << ws).opt(), ".." >> tag("=").opt(), (ws >> atom).opt())
    .spanned()
    .map(
        lambda x: Range(
            x[1], x[0][0], x[0][2], "clopen" if x[0][1] is None else "closed"
        )
    )
)

fn = (
    ((tag("fn") >> ws >> "(" >> (ws >> name).sep(ws * ",") << ws << ")") * (ws >> expr))
    .spanned()
    .map(lambda x: Fn(x[1], x[0][0], x[0][1]))
)

pre_exprs = recursive(
    lambda prefix: (((tag("!") + "~" + "-" + ":" + "...") << ws) * prefix)
    .spanned()
    .map(lambda x: Prefix(x[1], x[0][0], x[0][1]))
    + post_exprs
)

pow = right(pre_exprs, "**", BinOp)
mul = left(pow, "*" + "@" + "/" + "//" + "/^" + "%", BinOp)
add = left(mul, "+" + "-", BinOp)
shift = left(add, "<<" + ">>", BinOp)
bitand = left(shift, "&", BinOp)
bitxor = left(bitand, "^", BinOp)
bitor = left(bitxor, "|", BinOp)

expr.f = bitor
