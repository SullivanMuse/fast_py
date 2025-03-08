from dataclasses import dataclass, field

from instr import Instr
from mixins import Format, GetChildren


@dataclass
class ClosureSpec(Format):
    code: list[Instr]
    n_args: int
    capture_indices: list[int]

    def short(self):
        return f"{type(self).__qualname__}"

    def positional(self):
        yield from self.code


@dataclass
class Value(Format, GetChildren):
    def short(self):
        return f"Value.{type(self).__name__}"


@dataclass
class Unit(Value):
    pass


@dataclass
class Bool(Value):
    value: bool

    def positional(self):
        yield self.value


@dataclass
class Int(Value):
    value: int

    def positional(self):
        yield self.value


@dataclass
class Tag(Value):
    value: str


@dataclass
class String(Value):
    value: str

    def positional(self):
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

    def positional(self):
        yield from self.values


@dataclass
class Object(Value):
    values: dict[str, Value]

    def positional(self):
        yield from self.values.values()


@dataclass
class Closure(Value):
    spec: ClosureSpec
    captures: list[Value]

    @classmethod
    def from_code(cls, code):
        return cls(ClosureSpec(code, 0, []), [])


Value.get_children()
