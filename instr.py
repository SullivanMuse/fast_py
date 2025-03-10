from dataclasses import dataclass, asdict, fields

from mixins import Format, GetChildren


class Ref(Format, GetChildren):
    """Stack value offset"""


@dataclass
class Imm(Ref, Format):
    """Literal value"""

    value: "Value"

    def short(self):
        return f"imm"


@dataclass
class Stack(Ref, Format):
    """Stack slot"""

    index: int

    def short(self):
        return f"loc {self.index}"


@dataclass
class Arg(Ref, Format):
    """Function argument"""

    index: int

    def short(self):
        return f"arg {self.index}"


@dataclass
class Cap(Ref, Format):
    """Closure capture"""

    index: int

    def short(self):
        return f"cap {self.index}"


Ref.get_children()


@dataclass
class Instr(Format, GetChildren):
    def short(self):
        return f"Instr.{type(self).__name__}"


@dataclass
class Push(Instr):
    value: Ref


@dataclass
class ArrayPush(Instr):
    array: Ref
    value: Ref


@dataclass
class ArrayExtend(Instr):
    array_loc: Stack
    item_ref: Ref


@dataclass
class StringBufferPush(Instr):
    buffer_loc: Stack
    piece: Stack


@dataclass
class StringBufferToString(Instr):
    buffer_loc: Stack


@dataclass
class ClosureNew(Instr):
    spec: "ClosureSpec"


@dataclass
class Call(Instr):
    closure: Ref
    n_args: int


@dataclass
class LocalJump(Instr):
    condition: Ref
    dest: int


@dataclass
class Return(Instr):
    """Return from stack frame; return value is implicitly the top-most temporary on the previous stack frame"""


@dataclass
class Pop(Instr):
    # number of values to pop
    n: int


@dataclass
class Assert(Instr):
    value: Ref
    reason: str


@dataclass
class IsType(Instr):
    ty: type


@dataclass
class MatchArray(Instr):
    lower_bound: int


@dataclass
class Index(Instr):
    array: Ref
    ix: Ref


Instr.get_children()
