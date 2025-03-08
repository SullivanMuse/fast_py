from dataclasses import dataclass
from typing import Callable
from mixins import GetChildren
from value import ClosureSpec, Value


@dataclass
class Instr(GetChildren):
    def effect(self):
        """Effect on stack depth"""
        raise NotImplementedError


@dataclass
class GetLocal:
    """get local variable"""
    index: int

    def __str__(self):
        return f"  gloc {self.index}"

    def effect(self):
        return 1


@dataclass
class SetLocal:
    """set local variable"""
    index: int

    def __str__(self):
        return f"  sloc {self.index}"

    def effect(self):
        return -1


@dataclass
class Push(Instr):
    value: Value

    def __str__(self):
        return f"  push {self.value}"

    def effect(self):
        return 1


@dataclass
class Dupe(Instr):
    def __str__(self):
        return "  dup"

    def effect(self):
        return 1


@dataclass
class Pop(Instr):
    def __str__(self):
        return "  pop"

    def effect(self):
        return -1


@dataclass
class Jump(Instr):
    label: "Label"

    def __str__(self):
        return f"  jump '{self.label}"

    def effect(self):
        return 0


@dataclass
class JTrue(Instr):
    label: str

    def __str__(self):
        return f"  jtru '{self.label}"

    def effect(self):
        return -1


@dataclass
class Label(Instr):
    label: int

    def __str__(self):
        return f"'{self.label}:"

    def effect(self):
        return 0


@dataclass
class Ann(Instr):
    message: str

    def __str__(self):
        return f"  {repr(self.message)}"

    def effect(self):
        return 0


@dataclass
class Unary(Instr):
    op: Callable[[Value], Value]

    def __str__(self):
        return f"  unop {self.op.__name__}"

    def effect(self):
        return 0


@dataclass
class BinOp(Instr):
    op: Callable[[Value, Value], Value]

    def __str__(self):
        return f"  binop {self.op.__name__}"

    def effect(self):
        return -1


@dataclass
class JumpArrayNotMatch(Instr):
    n: int
    failure: str

    def __str__(self):
        return f"  janm {self.n} '{self.failure}"

    def effect(self):
        return 0


@dataclass
class JumpArrayMatch(Instr):
    n: int
    success: str

    def __str__(self):
        return f"  jam {self.n} '{self.success}"

    def effect(self):
        return 0


@dataclass
class Abort:
    reason: str

    def __str__(self):
        return f"  abort {repr(self.reason)}"

    def effect(self):
        return 0


@dataclass
class MakeClosure:
    label: str
    slots: int

    def __str__(self):
        return f"  clos '{self.label} {self.slots}"

    def effect(self):
        return 1


@dataclass
class CapLoc:
    """capture local variable and add to closure object"""
    index: int

    def __str__(self):
        return f"  capl {self.index}"

    def effect(self):
        return 0


@datacass
class CapCap:
    """capture capture and add to closure object"""
    index: int

    def __str__(self):
        return f"  capc {self.index}"

    def effect(self):
        return 0


@dataclass
class GetCap:
    """get capture from current function"""
    index: int

    def __str__(self):
        return f"  gcap {self.index}"

    def effect(self):
        return 1


@dataclass
class SetCap:
    """set capture in current function"""
    index: int

    def __str__(self):
        return f"  scap {self.index}"

    def effect(self):
        return -1


Instr.get_children()
