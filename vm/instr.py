# builtin
from dataclasses import dataclass, field
from enum import auto, Enum
from typing import Any

# project
from format_node import FormatNode
from vm.value import Value


@dataclass
class Im(FormatNode):
    value: Value

    def str(self):
        return f"im {self.value}"

    @property
    def children(self):
        return ()


@dataclass
class Loc(FormatNode):
    index: int

    def str(self):
        return f"loc {self.index}"

    @property
    def children(self):
        return ()


class InstrTy(Enum):
    Push = auto() # Push a literal value
    Call = auto() # Call a closure

    # Array
    Array = auto() # Create an array 1 ->
    ArrayPush = auto() # Push an element into an array


@dataclass
class Instr(FormatNode):
    ty: InstrTy
    children: list[Im | Loc] = field(default_factory=list)

    def str(self):
        return f"{self.ty.name}"
