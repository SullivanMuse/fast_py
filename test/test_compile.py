from comb import Span
from compile import compile
from instr import (
    ArrayExtend,
    ArrayPush,
    Assert,
    Call,
    Imm,
    Local,
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
            Push(value=Imm(value=StringBuffer(pieces=[Local(index=0)]))),
            Push(value=Imm(value=Int(value=123))),
            StringBufferPush(buffer_loc=Local(index=1), piece=Local(index=2)),
            Push(value=Imm(value=String(value="asdf"))),
            StringBufferPush(buffer_loc=Local(index=1), piece=Local(index=3)),
            StringBufferToString(buffer_loc=Local(index=1)),
        ],
    )
    code_test(
        '"asdf{"asdf"}asdf"',
        [
            Push(value=Imm(value=String(value="asdf"))),
            Push(value=Imm(value=StringBuffer(pieces=[Local(index=0)]))),
            Push(value=Imm(value=String(value="asdf"))),
            StringBufferPush(buffer_loc=Local(index=1), piece=Local(index=2)),
            Push(value=Imm(value=String(value="asdf"))),
            StringBufferPush(buffer_loc=Local(index=1), piece=Local(index=3)),
            StringBufferToString(buffer_loc=Local(index=1)),
        ],
    )
    code_test(
        'let x = 12; x"Hello"',
        [
            Push(value=Imm(value=Int(value=12))),
            Push(value=Bool(value=True)),
            Assert(
                value=Local(index=1), reason="Irrefutable pattern: IdPattern 4:5 'x'"
            ),
            Push(value=Imm(value=String(value="Hello"))),
            Push(value=Local(index=0)),
            Call(closure=Local(index=0)),
        ],
        is_expr=False,
    )


def test_compile_array():
    code_test(
        "[1, 2, 3]",
        [
            Push(value=Array(values=[None, None, None])),
            Push(value=Imm(value=Int(value=1))),
            ArrayPush(array=Local(index=0), value=Local(index=1)),
            Push(value=Imm(value=Int(value=2))),
            ArrayPush(array=Local(index=0), value=Local(index=1)),
            Push(value=Imm(value=Int(value=3))),
            ArrayPush(array=Local(index=0), value=Local(index=1)),
        ],
    )

    code_test(
        "[1, 2, ...[3, 4]]",
        [
            Push(value=Array(values=[None, None, None])),
            Push(value=Imm(value=Int(value=1))),
            ArrayPush(array=Local(index=0), value=Local(index=1)),
            Push(value=Imm(value=Int(value=2))),
            ArrayPush(array=Local(index=0), value=Local(index=1)),
            Push(value=Array(values=[None, None])),
            Push(value=Imm(value=Int(value=3))),
            ArrayPush(array=Local(index=1), value=Local(index=2)),
            Push(value=Imm(value=Int(value=4))),
            ArrayPush(array=Local(index=1), value=Local(index=2)),
            ArrayExtend(array_loc=Local(index=0), item_ref=Local(index=1)),
        ],
    )


def test_fn_expr():
    code_test("fn() {()}", [Push(value=Imm(value=Unit()))])

    # code_test(
    #     "fn(x, y, z) { x(y, z); }",
    # )
