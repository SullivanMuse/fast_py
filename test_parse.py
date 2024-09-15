from comb import Input, Span
from expr import *
from parse import *


def test_integer():
    s = "1234"
    assert integer(s) == (Integer(Span.all(s)), Input.end(s)), "Successful parse"

    s = "123_456"
    assert integer(s) == (Integer(Span.all(s)), Input.end(s)), "Successful parse"

    s = "_123"
    assert integer(s) is None, "Unsuccesful parse"

    s = ""
    assert integer(s) is None, "Unsuccesful parse"


def test_float():
    s = "1234"
    assert floating(s) is None, "Unsuccessful parse"

    s = "1.0"
    assert floating(s) == (Float(Span.all(s)), Input.end(s)), "Successful parse"

    s = "1e5"
    assert floating(s) == (Float(Span.all(s)), Input.end(s)), "Successful parse"

    s = "1.0e-5"
    assert floating(s) == (Float(Span.all(s)), Input.end(s)), "Successful parse"


def test_ident():
    s = "asdf"
    assert id(s) == (Id(Span.all(s)), Input.end(s)), "Successful parse"

    s = "Hello123"
    assert id(s) == (Id(Span.all(s)), Input.end(s)), "Successful parse"

    s = "1234asdf"
    assert id(s) is None, "Unsuccessful parse"


def test_string():
    s = '"Hello"'
    assert string(s) == (
        String(
            Span.all(s),
            None,
            [
                Span(s, 1, 2),
                Span(s, 2, 3),
                Span(s, 3, 4),
                Span(s, 4, 5),
                Span(s, 5, 6),
            ],
        ),
        Input.end(s),
    ), "Basic string"

    s = 'd"2024-09-01"'
    assert string(s) == (
        String(
            Span.all(s),
            Id(Span(s, 0, 1)),
            [
                Span(s, 2, 3),
                Span(s, 3, 4),
                Span(s, 4, 5),
                Span(s, 5, 6),
                Span(s, 6, 7),
                Span(s, 7, 8),
                Span(s, 8, 9),
                Span(s, 9, 10),
                Span(s, 10, 11),
                Span(s, 11, 12),
            ],
        ),
        Input.end(s),
    ), "String with modifier"

    s = '"Hello, {there}"'
    assert string(s) == (
        String(
            Span.all(s),
            None,
            [
                Span(s, 1, 2),
                Span(s, 2, 3),
                Span(s, 3, 4),
                Span(s, 4, 5),
                Span(s, 5, 6),
                Span(s, 6, 7),
                Span(s, 7, 8),
                Id(Span(s, 9, 14)),
            ],
        ),
        Input.end(s),
    ), "String with interpolant"

    s = '"Hello\\\\!"'
    assert string(s) == (
        String(
            Span.all(s),
            None,
            [
                Span(s, 1, 2),
                Span(s, 2, 3),
                Span(s, 3, 4),
                Span(s, 4, 5),
                Span(s, 5, 6),
                Span(s, 6, 8),
                Span(s, 8, 9),
            ],
        ),
        Input.end(s),
    ), "String with escape"


def test_array():
    s = "[]"
    assert array(s) == (
        Array(Span.all(s), [], "[", "]"),
        Input.end(s),
    ), "Array with no elements"

    s = "[1]"
    assert array(s) == (
        Array(Span.all(s), [Integer(Span(s, 1, 2))], "[", "]"),
        Input.end(s),
    ), "Array with single element"

    # TODO:
    #   s = "[1, 2]"
    #   s = "[1, 2,]"


def test_range():
    s = ".."
    assert range_syntax(s) == (
        Range(Span.all(s), None, None, "clopen"),
        Input.end(s),
    ), "Range all clopen"

    s = "..="
    assert range_syntax(s) == (
        Range(Span.all(s), None, None, "closed"),
        Input.end(s),
    ), "Range all closed"

    s = "a..="
    assert range_syntax(s) == (
        Range(Span.all(s), Id(Span(s, 0, 1)), None, "closed"),
        Input.end(s),
    ), "Range from closed"

    s = "a.."
    assert range_syntax(s) == (
        Range(Span.all(s), Id(Span(s, 0, 1)), None, "clopen"),
        Input.end(s),
    ), "Range from clopen"

    s = "..=b"
    assert range_syntax(s) == (
        Range(Span.all(s), None, Id(Span(s, len(s) - 1, len(s))), "closed"),
        Input.end(s),
    ), "Range to closed"

    s = "..b"
    assert range_syntax(s) == (
        Range(Span.all(s), None, Id(Span(s, len(s) - 1, len(s))), "clopen"),
        Input.end(s),
    ), "Range to clopen"

    s = " .."
    assert range_syntax(s) is None, "Bad whitespace"

    s = " ..="
    assert range_syntax(s) is None, "Bad whitespace"

    s = "a ..="
    assert range_syntax(s) == (
        Range(Span.all(s), Id(Span(s, 0, 1)), None, "closed"),
        Input.end(s),
    ), "Range from closed with whitespace"

    s = "a .."
    assert range_syntax(s) == (
        Range(Span.all(s), Id(Span(s, 0, 1)), None, "clopen"),
        Input.end(s),
    ), "Range from clopen with whitespace"

    s = "..= b"
    assert range_syntax(s) == (
        Range(Span.all(s), None, Id(Span(s, len(s) - 1, len(s))), "closed"),
        Input.end(s),
    ), "Range to closed with whitespace"

    s = ".. b"
    assert range_syntax(s) == (
        Range(Span.all(s), None, Id(Span(s, len(s) - 1, len(s))), "clopen"),
        Input.end(s),
    ), "Range to clopen with whitespace"


def test_fn():
    s = "fn(a,b,c) a"
    assert fn(s) == (
        Fn(
            Span.all(s),
            [Span(s, 3, 4), Span(s, 5, 6), Span(s, 7, 8)],
            Id(Span(s, len(s) - 1, len(s))),
        ),
        Input.end(s),
    ), "Successful parse"

    s = "fn ( a , b , c , ) a"
    assert fn(s) == (
        Fn(
            Span.all(s),
            [Span(s, 5, 6), Span(s, 9, 10), Span(s, 13, 14)],
            Id(Span(s, len(s) - 1, len(s))),
        ),
        Input.end(s),
    ), "Successful parse"


def test_paren():
    s = "(x)"
    assert paren(s) == (
        Paren(Span.all(s), Id(Span(s, 1, 2)), "(", ")"),
        Input.end(s),
    ), "Successful parse"

    s = "( x )"
    assert paren(s) == (
        Paren(Span.all(s), Id(Span(s, 2, 3)), "(", ")"),
        Input.end(s),
    ), "Successful parse"

    s = "( (x) )"
    assert paren(s) == (
        Paren(Span.all(s), Paren(Span(s, 2, 5), Id(Span(s, 3, 4)), "(", ")"), "(", ")"),
        Input.end(s),
    ), "Successful parse"


def test_post_exprs():
    s = "x.y(a)[c].await.chain?"
    id_x = Id(Span(s, i=0, j=1))
    field_y = Field(Span(s, i=0, j=3), id_x, Span(s, i=2, j=3))
    call = Call(Span(s, i=0, j=6), field_y, Id(Span(s, i=4, j=5)))
    index = Index(Span(s, i=0, j=9), call, Id(Span(s, i=7, j=8)))
    await_ = Await(Span(s, i=0, j=15), index)
    chain = Chain(Span(s, i=0, j=21), await_)
    propogate = Propogate(Span(s, i=0, j=22), chain)
    assert post_exprs(s) == (
        propogate,
        Input.end(s),
    ), "Successful parse"


def test_pre_exprs():
    s = "...!~-:x"
    id_x = Id(Span(s, i=7, j=8))
    quote = Prefix(Span(s, i=6, j=8), ":", id_x)
    negative = Prefix(Span(s, i=5, j=8), "-", quote)
    complement = Prefix(Span(s, i=4, j=8), "~", negative)
    not_ = Prefix(Span(s, i=3, j=8), "!", complement)
    spread = Prefix(Span.all(s), "...", not_)
    assert pre_exprs(s) == (spread, Input.end(s)), "Successful parse"


def test_range_syntax():
    s = "x..y"
    assert range_syntax(s) == (Range(Span.all(s), Id(Span(s, 0, 1)), Id(Span(s, 3, 4)), "clopen"), Input.end(s)), "Successful parse"
    
    s = "x..=y"
    assert range_syntax(s) == (Range(Span.all(s), Id(Span(s, 0, 1)), Id(Span(s, 4, 5)), "closed"), Input.end(s)), "Successful parse"


def test_pow():
    s = "x**y"
    assert pow(s) == (BinOp(Span.all(s), "**", Id(Span(s, 0, 1)), Id(Span(s, 3, 4))), Input.end(s)), "Successful parse"


def test_lam():
    s = "fn(x) x"
    assert fn(s) == (Fn(Span.all(s), [Span(s, 3, 4)], Id(Span(s, len(s) - 1, len(s)))), Input.end(s)), "Successful parse"

def test_binop():
    for op in ["*", "@", "/", "%", "+", "-", "&", "^", "|"]:
        s = f"x{op}x"
        assert expr(s) == (BinOp(Span(s, 0, 3), op, Id(Span(s, 0, 1)), Id(Span(s, 2, 3))), Input(s, 3)), "Successful parse"
    
    for op in ["//", "/^", "<<", ">>"]:
        s = f"x{op}x"
        assert expr(s) == (BinOp(Span(s, 0, 4), op, Id(Span(s, 0, 1)), Id(Span(s, 3, 4))), Input(s, 4)), "Successful parse"

def test_comparison():
    s = "1 is 2 isnot 3 in 4 notin 5 <= 6 >= 7 < 8 > 9 == 10 != 11"
    
    r = (Comparison(span=Span(s='1 is 2 isnot 3 in 4 notin 5 <= 6 >= 7 < 8 > 9 == 10 != 11', i=0, j=57), ops=['is', 'isnot', 'in', 'notin', '<=', '>=', '<', '>', '==', '!='], inner=[Integer(span=Span(s='1 is 2 isnot 3 in 4 notin 5 <= 6 >= 7 < 8 > 9 == 10 != 11', i=0, j=1)), Integer(span=Span(s='1 is 2 isnot 3 in 4 notin 5 <= 6 >= 7 < 8 > 9 == 10 != 11', i=5, j=6)), Integer(span=Span(s='1 is 2 isnot 3 in 4 notin 5 <= 6 >= 7 < 8 > 9 == 10 != 11', i=13, j=14)), Integer(span=Span(s='1 is 2 isnot 3 in 4 notin 5 <= 6 >= 7 < 8 > 9 == 10 != 11', i=18, j=19)), Integer(span=Span(s='1 is 2 isnot 3 in 4 notin 5 <= 6 >= 7 < 8 > 9 == 10 != 11', i=26, j=27)), Integer(span=Span(s='1 is 2 isnot 3 in 4 notin 5 <= 6 >= 7 < 8 > 9 == 10 != 11', i=31, j=32)), Integer(span=Span(s='1 is 2 isnot 3 in 4 notin 5 <= 6 >= 7 < 8 > 9 == 10 != 11', i=36, j=37)), Integer(span=Span(s='1 is 2 isnot 3 in 4 notin 5 <= 6 >= 7 < 8 > 9 == 10 != 11', i=40, j=41)), Integer(span=Span(s='1 is 2 isnot 3 in 4 notin 5 <= 6 >= 7 < 8 > 9 == 10 != 11', i=44, j=45)), Integer(span=Span(s='1 is 2 isnot 3 in 4 notin 5 <= 6 >= 7 < 8 > 9 == 10 != 11', i=49, j=51)), Integer(span=Span(s='1 is 2 isnot 3 in 4 notin 5 <= 6 >= 7 < 8 > 9 == 10 != 11', i=55, j=57))]), Input(s='1 is 2 isnot 3 in 4 notin 5 <= 6 >= 7 < 8 > 9 == 10 != 11', i=57))
    assert comparison(s) == r, "Successful parse"

def test_boolean():
    s = "a and b or c and d"
    r = (BinOp(span=Span(s='a and b or c and d', i=0, j=18), op='or', left=BinOp(span=Span(s='a and b or c and d', i=0, j=7), op='and', left=Id(span=Span(s='a and b or c and d', i=0, j=1)), right=Id(span=Span(s='a and b or c and d', i=6, j=7))), right=BinOp(span=Span(s='a and b or c and d', i=11, j=18), op='and', left=Id(span=Span(s='a and b or c and d', i=11, j=12)), right=Id(span=Span(s='a and b or c and d', i=17, j=18)))), Input(s='a and b or c and d', i=18))
    assert expr(s) == r, "Successful parse"


def test_statements():
    s = "x;y; {} x"
    r = (Statements(statements=[Id(span=Span(s='x;y; {} x', i=0, j=1)), Id(span=Span(s='x;y; {} x', i=2, j=3)), Statements(statements=[], final_semicolon=False), Id(span=Span(s='x;y; {} x', i=8, j=9))], final_semicolon=False), Input(s='x;y; {} x', i=9))
    assert statements(s) == r, "Successful parse"


def test_if():
    s = "if x { y } else if 5 { z }"
    r = (If(span=Span(s='if x { y } else if 5 { z }', i=0, j=26), predicate=Id(span=Span(s='if x { y } else if 5 { z }', i=3, j=4)), consequence=Statements(statements=[Id(span=Span(s='if x { y } else if 5 { z }', i=7, j=8))], final_semicolon=False), alternative=If(span=Span(s='if x { y } else if 5 { z }', i=16, j=26), predicate=Integer(span=Span(s='if x { y } else if 5 { z }', i=19, j=20)), consequence=Statements(statements=[Id(span=Span(s='if x { y } else if 5 { z }', i=23, j=24))], final_semicolon=False), alternative=None)), Input(s='if x { y } else if 5 { z }', i=26))
    assert if_stmt(s) == r, "Successful parse"


def test_let():
    s = "let x = 5"
    r = (Let(span=Span(s='let x = 5', i=0, j=9), pattern=Span(s='let x = 5', i=4, j=5), inner=Integer(span=Span(s='let x = 5', i=8, j=9))), Input(s='let x = 5', i=9))
    assert let(s) == r, "Successful parse"


def test_assign():
    s = "x = 5"
    r = (Assign(span=Span(s='x = 5', i=0, j=5), pattern=Span(s='x = 5', i=0, j=1), expression=Integer(span=Span(s='x = 5', i=4, j=5))), Input(s='x = 5', i=5))
    assert assign(s) == r, "Successful parse"


def test_use():
    s = "use x.(y, z as w, )"
    r = (Use(span=Span(s='use x.(y, z as w, )', i=0, j=19), path=Path(parents=[Span(s='use x.(y, z as w, )', i=4, j=5)], terminator=PathListTerminator(paths=[Path(parents=[], terminator=SimpleTerminator(name=Span(s='use x.(y, z as w, )', i=7, j=8), rename=None)), Path(parents=[], terminator=SimpleTerminator(name=Span(s='use x.(y, z as w, )', i=10, j=11), rename=Span(s='use x.(y, z as w, )', i=15, j=16)))]))), Input(s='use x.(y, z as w, )', i=19))
    assert use(s) == r, "Successful parse"


def test_fn_name():
    s = "fn name(a, b, c) e"
    r = (FnNamed(span=Span(s='fn name(a, b, c) e', i=0, j=18), name=Span(s='fn name(a, b, c) e', i=3, j=7), args=[Span(s='fn name(a, b, c) e', i=8, j=9), Span(s='fn name(a, b, c) e', i=11, j=12), Span(s='fn name(a, b, c) e', i=14, j=15)], expr=Id(span=Span(s='fn name(a, b, c) e', i=17, j=18))), Input(s='fn name(a, b, c) e', i=18))
    assert fn_stmt(s) == r, "Successful parse"

    s = "fn name( a , b , c , ) a"
    r = (FnNamed(span=Span(s='fn name( a , b , c , ) a', i=0, j=24), name=Span(s='fn name( a , b , c , ) a', i=3, j=7), args=[Span(s='fn name( a , b , c , ) a', i=9, j=10), Span(s='fn name( a , b , c , ) a', i=13, j=14), Span(s='fn name( a , b , c , ) a', i=17, j=18)], expr=Id(span=Span(s='fn name( a , b , c , ) a', i=23, j=24))), Input(s='fn name( a , b , c , ) a', i=24))
    assert fn_stmt(s) == r, "Successful parse"
