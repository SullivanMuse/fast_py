from compile import compile
from instr import Imm, Push
from value import Closure, ClosureSpec, Float, Int, String, Tag


def code_test(expr, code, message=None):
    result = compile(expr)
    if message is None:
        message = f"{expr} should compile to {code}"
    assert result == Closure(
        spec=ClosureSpec(code=code, n_args=0, capture_indices=[]), captures=[]
    ), message


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
    code_test('"x{123}y"', [Push(value=Imm(value=String(value="x123y")))])
