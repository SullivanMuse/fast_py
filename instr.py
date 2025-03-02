from dataclasses import dataclass

from mixins import FormatNode, GetChildren


class Ref(FormatNode, GetChildren):
    """Stack value offset"""


@dataclass
class Imm(Ref, FormatNode):
    """Literal value"""

    value: "Value"

    def short(self):
        return f"imm"

    def children(self):
        yield self.value


@dataclass
class Loc(Ref, FormatNode):
    index: int

    def short(self):
        return f"loc {self.index}"


Ref.get_children()


@dataclass
class Instr(FormatNode, GetChildren):
    def short(self):
        return f"Instr.{type(self).__name__}"


@dataclass
class Push(Instr):
    value: Ref

    def children(self):
        yield self.value


@dataclass
class ArrayPush(Instr):
    array: Ref
    value: Ref


@dataclass
class ArrayExtend(Instr):
    array_loc: Loc
    item_ref: Ref


@dataclass
class StringBufferPush(Instr):
    buffer_loc: Loc
    piece: Loc


@dataclass
class StringBufferToString(Instr):
    buffer_loc: Loc


@dataclass
class ClosureNew(Instr):
    spec: "ClosureSpec"


@dataclass
class Call(Instr):
    closure: Ref


@dataclass
class Jump(Instr):
    condition: Ref
    dest: int


@dataclass
class Return(Instr):
    """Return from stack frame; return value is implicitly the top-most temporary on the previous stack frame"""


@dataclass
class Pop(Instr):
    pass


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
