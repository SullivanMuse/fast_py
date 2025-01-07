from dataclasses import dataclass

from format_node import FormatNode
from vm.instr import Instr


@dataclass
class ClosureSpec:
    code: list[Instr]
    args: int
    captures: list[int]


@dataclass
class Value(FormatNode):
    def str(self):
        return f"Value.{type(self).__name__}"

    @property
    def children(self):
        return []


@dataclass
class Unit(Value):
    pass


@dataclass
class Int(Value):
    value: int


@dataclass
class Tag(Value):
    value: str


@dataclass
class Float(Value):
    value: float


@dataclass
class Array(Value):
    values: list[Value]

    @property
    def children(self):
        return self.values


@dataclass
class Object(Value):
    values: dict[str, Value]

    @property
    def children(self):
        return list(self.values.values())


@dataclass
class Closure(Value):
    spec: ClosureSpec
    captures: list[Value]

    @property
    def children(self):
        return self.captures
