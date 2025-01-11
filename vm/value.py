from dataclasses import dataclass, field

from mixins import FormatNode, GetChildren
from vm.instr import Instr


@dataclass
class ClosureSpec:
    code: list[Instr]
    n_args: int
    captures: list[int]


@dataclass
class Value(FormatNode, GetChildren):
    def str(self):
        return f"Value.{type(self).__name__}"

    @property
    def children(self):
        return []


@dataclass
class Unit(Value):
    pass


@dataclass
class Bool(Value):
    value: bool


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
    values: list[Value] = field(default_factory=list)

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


Value.get_children()
