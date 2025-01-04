from dataclasses import dataclass, field
from enum import auto, Enum

from format_node import FormatNode


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

    @classmethod
    def closure(cls, code=list, captures=list["Value"]):
        return cls(ValueTy.Closure, [code, captures])
