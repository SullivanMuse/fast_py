from dataclasses import dataclass, field
from enum import auto, Enum

from format_node import FormatNode


class ValueSpec:
    pass


@dataclass
class Imm(ValueSpec, FormatNode):
    value: "Value"

    def str(self):
        return f"im {self.value}"

    @property
    def children(self):
        return ()


@dataclass
class Loc(ValueSpec, FormatNode):
    index: int

    def str(self):
        return f"loc {self.index}"

    @property
    def children(self):
        return ()


class InstrTy(Enum):
    Push = auto()  # Push a literal value

    # Array
    Array = auto()  # Create an array 1 ->
    ArrayPush = auto()  # Push an element into an array

    # Closure
    Closure = auto()  # Create a closure
    Call = auto()  # Call a closure


@dataclass
class Instr(FormatNode):
    ty: InstrTy
    children: list[Imm | Loc] = field(default_factory=list)

    def str(self):
        return f"{self.ty.name}"
