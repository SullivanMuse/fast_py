# builtin
from dataclasses import dataclass, field
from enum import auto, Enum


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
class Value:
    ty: ValueTy
    children: list["Value"] = field(default_factory=list)

    @classmethod
    def closure(cls, code=list["Instr"], captures=list["Value"]):
        return cls(ValueTy.Closure, [code, captures])
