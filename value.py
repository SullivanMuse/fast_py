from dataclasses import dataclass, field

from instr import Instr
from mixins import FormatNode


@dataclass
class ClosureSpec(FormatNode):
    code: list[Instr]
    n_args: int
    capture_indices: list[int]

    def short(self):
        return f"{type(self).__qualname__}"

    def children(self):
        yield from self.code


@dataclass
class Value(FormatNode):
    def short(self):
        return f"Value.{type(self).__name__}"


@dataclass
class Unit(Value):
    pass


@dataclass
class Bool(Value):
    value: bool

    def children(self):
        yield self.value


@dataclass
class Int(Value):
    value: int


@dataclass
class Tag(Value):
    value: str


@dataclass
class String(Value):
    value: str

    def children(self):
        yield self.value


@dataclass
class StringBuffer(Value):
    pieces: list[String]


@dataclass
class Float(Value):
    value: float


@dataclass
class Array(Value):
    values: list[Value] = field(default_factory=list)

    def children(self):
        yield from self.values


@dataclass
class Object(Value):
    values: dict[str, Value]

    def children(self):
        yield from self.values.values()


@dataclass
class Closure(Value):
    spec: ClosureSpec
    captures: list[Value]

    @classmethod
    def from_code(cls, code):
        return cls(ClosureSpec(code, 0, []), [])

    def children(self):
        yield self.spec
        yield from self.captures
