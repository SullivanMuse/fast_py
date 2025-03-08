import dataclasses
import typing

import mixins
import value


@dataclasses.dataclass
class Instr(mixins.GetChildren):
    def effect(self):
        """Effect on stack depth"""
        raise NotImplementedError


@dataclasses.dataclass
class GetLocal:
    """get local variable"""
    index: int

    def __str__(self):
        return f"  gloc {self.index}"

    def effect(self):
        return 1


@dataclasses.dataclass
class SetLocal:
    """set local variable"""
    index: int

    def __str__(self):
        return f"  sloc {self.index}"

    def effect(self):
        return -1


@dataclasses.dataclass
class Push(Instr):
    value: value.Value

    def __str__(self):
        return f"  push {self.value}"

    def effect(self):
        return 1


@dataclasses.dataclass
class Dupe(Instr):
    def __str__(self):
        return "  dup"

    def effect(self):
        return 1


@dataclasses.dataclass
class Pop(Instr):
    def __str__(self):
        return "  pop"

    def effect(self):
        return -1


@dataclasses.dataclass
class Jump(Instr):
    label: "Label"

    def __str__(self):
        return f"  jump '{self.label}"

    def effect(self):
        return 0


@dataclasses.dataclass
class JTrue(Instr):
    label: str

    def __str__(self):
        return f"  jtru '{self.label}"

    def effect(self):
        return -1


@dataclasses.dataclass
class Label(Instr):
    label: int

    def __str__(self):
        return f"'{self.label}:"

    def effect(self):
        return 0


@dataclasses.dataclass
class Ann(Instr):
    message: str

    def __str__(self):
        return f"  {repr(self.message)}"

    def effect(self):
        return 0


@dataclasses.dataclass
class Unary(Instr):
    op: typing.Callable[[value.Value], value.Value]

    def __str__(self):
        return f"  unop {self.op.__name__}"

    def effect(self):
        return 0


@dataclasses.dataclass
class BinOp(Instr):
    op: typing.Callable[[value.Value, value.Value], value.Value]

    def __str__(self):
        return f"  binop {self.op.__name__}"

    def effect(self):
        return -1


@dataclasses.dataclass
class JumpArrayNotMatch(Instr):
    n: int
    failure: str

    def __str__(self):
        return f"  janm {self.n} '{self.failure}"

    def effect(self):
        return 0


@dataclasses.dataclass
class JumpArrayMatch(Instr):
    n: int
    success: str

    def __str__(self):
        return f"  jam {self.n} '{self.success}"

    def effect(self):
        return 0


@dataclasses.dataclass
class Abort:
    reason: str

    def __str__(self):
        return f"  abort {repr(self.reason)}"

    def effect(self):
        return 0


@dataclasses.dataclass
class MakeClosure:
    code: list[Instr]
    n_args: int
    slots: int

    def __str__(self):
        return f"  clos '{self.label} {self.slots}"

    def effect(self):
        return 1


@dataclasses.dataclass
class CapLoc:
    """capture local variable and add to closure object"""
    index: int

    def __str__(self):
        return f"  capl {self.index}"

    def effect(self):
        return 0


@dataclasses.dataclass
class CapCap:
    """capture capture and add to closure object"""
    index: int

    def __str__(self):
        return f"  capc {self.index}"

    def effect(self):
        return 0


@dataclasses.dataclass
class GetCap:
    """get capture from current function"""
    index: int

    def __str__(self):
        return f"  gcap {self.index}"

    def effect(self):
        return 1


@dataclasses.dataclass
class SetCap:
    """set capture in current function"""
    index: int

    def __str__(self):
        return f"  scap {self.index}"

    def effect(self):
        return -1


Instr.get_children()
