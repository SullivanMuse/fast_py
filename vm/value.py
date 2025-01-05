from dataclasses import dataclass, field
from enum import auto, Enum

from format_node import FormatNode
from vm.instr import Instr


class ValueTy(Enum):
    # basic
    Unit = auto()
    Int = auto()
    Tag = auto()
    Float = auto()

    # aggregates
    Array = auto()
    Object = auto()
    Closure = auto()


@dataclass
class Value(FormatNode):
    ty: ValueTy
    children: list["Value"] = field(default_factory=list)

    def str(self):
        return f"{self.ty.name}"


@dataclass
class ClosureSpec:
    code: list[Instr]
    args: int
    captures: list[int]


@dataclass
class Closure:
    spec: ClosureSpec
    captures: list[Value]
