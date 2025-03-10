from comb import Span
from compile import compile
from instr import (
    Arg,
    ArrayExtend,
    ArrayPush,
    Assert,
    Call,
    ClosureNew,
    Imm,
    Stack,
    Push,
    StringBufferPush,
    StringBufferToString,
)
from value import (
    Array,
    Bool,
    Closure,
    ClosureSpec,
    Float,
    Int,
    String,
    StringBuffer,
    Tag,
    Unit,
)


def code_test(expr, code, message=None, depth=1, is_expr=True):
    result = compile(expr)
    if message is None:
        message = f"{expr} should compile to {code}"
    assert result == Closure(
        spec=ClosureSpec(code=code, n_args=0, capture_indices=[]), captures=[]
    ), message

    if is_expr and depth != 0:
        code_test(f"({expr})", code, depth=depth - 1)


def test_compile_int():
    code_test("123", [Push(value=Imm(value=Int(value=123)))])


def test_compile_float():
    code_test("123.456", [Push(value=Imm(value=Float(value=123.456)))])
    code_test("123.456e789", [Push(value=Imm(value=Float(value=float("inf"))))])
    code_test("123e10", [Push(value=Imm(value=Float(value=123e10)))])


def test_compile_tag():
    code_test(":asdf", [Push(value=Imm(value=Tag(value=":asdf")))])


def test_compile_string():
    code_test('"asdf"', [Push(value=Imm(value=String(value="asdf")))])
    code_test(
        '"asdf{123}asdf"',
        [
            Push(value=Imm(value=String(value="asdf"))),
            Push(value=Imm(value=StringBuffer(pieces=[Stack(index=0)]))),
            Push(value=Imm(value=Int(value=123))),
            StringBufferPush(buffer_loc=Stack(index=1), piece=Stack(index=2)),
            Push(value=Imm(value=String(value="asdf"))),
            StringBufferPush(buffer_loc=Stack(index=1), piece=Stack(index=3)),
            StringBufferToString(buffer_loc=Stack(index=1)),
        ],
    )
    code_test(
        '"asdf{"asdf"}asdf"',
        [
            Push(value=Imm(value=String(value="asdf"))),
            Push(value=Imm(value=StringBuffer(pieces=[Stack(index=0)]))),
            Push(value=Imm(value=String(value="asdf"))),
            StringBufferPush(buffer_loc=Stack(index=1), piece=Stack(index=2)),
            Push(value=Imm(value=String(value="asdf"))),
            StringBufferPush(buffer_loc=Stack(index=1), piece=Stack(index=3)),
            StringBufferToString(buffer_loc=Stack(index=1)),
        ],
    )
    code_test(
        'let f = fn(x) x; f"hello"',
        [
            ClosureNew(
                spec=ClosureSpec(
                    code=[Push(value=Arg(index=0))], n_args=1, capture_indices=[]
                )
            ),
            Push(value=Imm(value=Bool(value=True))),
            Assert(
                value=Stack(index=1), reason="Irrefutable pattern: IdPattern 4:5 'f'"
            ),
            Push(value=Stack(index=0)),
            Push(value=Imm(value=String(value="hello"))),
            Call(closure=Stack(index=2), n_args=1),
        ],
        is_expr=False,
    )

    assert compile('let f = fn(x) x; f"hello"') == compile(
        'let f = fn(x) x; f("hello")'
    ), "prefix function is the same"


def test_compile_array():
    code_test(
        "[1, 2, 3]",
        [
            Push(value=Array(values=[None, None, None])),
            Push(value=Imm(value=Int(value=1))),
            ArrayPush(array=Stack(index=0), value=Stack(index=1)),
            Push(value=Imm(value=Int(value=2))),
            ArrayPush(array=Stack(index=0), value=Stack(index=1)),
            Push(value=Imm(value=Int(value=3))),
            ArrayPush(array=Stack(index=0), value=Stack(index=1)),
        ],
    )

    code_test(
        "[1, 2, ...[3, 4]]",
        [
            Push(value=Array(values=[None, None, None])),
            Push(value=Imm(value=Int(value=1))),
            ArrayPush(array=Stack(index=0), value=Stack(index=1)),
            Push(value=Imm(value=Int(value=2))),
            ArrayPush(array=Stack(index=0), value=Stack(index=1)),
            Push(value=Array(values=[None, None])),
            Push(value=Imm(value=Int(value=3))),
            ArrayPush(array=Stack(index=1), value=Stack(index=2)),
            Push(value=Imm(value=Int(value=4))),
            ArrayPush(array=Stack(index=1), value=Stack(index=2)),
            ArrayExtend(array_loc=Stack(index=0), item_ref=Stack(index=1)),
        ],
    )


def test_fn_expr():
    code_test("fn() {()}", [Push(value=Imm(value=Unit()))])

    code_test(
        "fn(x, y, z) { x(y, z); }",
        [
            ClosureNew(
                spec=ClosureSpec(
                    code=[
                        Push(value=Arg(index=0)),
                        Push(value=Arg(index=1)),
                        Push(value=Arg(index=2)),
                        Call(closure=Stack(index=0), n_args=2),
                    ],
                    n_args=3,
                    capture_indices=[],
                )
            )
        ],
    )
