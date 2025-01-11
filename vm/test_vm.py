from vm.instr import ArrayPush, Imm, Loc, Push, Return
from vm.value import Array, Closure, ClosureSpec, Unit
from vm.vm import Vm


def test_vm():
    code = [
        Push(Imm(Array())),
        ArrayPush(Loc(0), Imm(Unit())),
        Return(Loc(0)),
    ]
    closure = Closure.from_code(code)
    vm = Vm()
    assert vm.run(closure) == Array([Unit()]), "bad return value"
    assert vm == Vm(), "bad final vm state"
