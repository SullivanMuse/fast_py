from dataclasses import dataclass

from mixins import FormatNode, GetChildren


class Ref(GetChildren):
    @property
    def children(self):
        return ()


@dataclass
class Imm(Ref, FormatNode):
    value: "Value"

    def str(self):
        return f"imm {self.value}"


@dataclass
class Loc(Ref, FormatNode):
    index: int

    def str(self):
        return f"loc {self.index}"


Ref.get_children()


@dataclass
class Instr(FormatNode, GetChildren):
    def str(self):
        return f"Instr.{type(self).__name__}"

    @classmethod
    def _get_classes(cls):
        for sub in cls.__subclasses__():
            setattr(cls, sub.__name__, sub)


@dataclass
class Push(Instr):
    value: Ref


@dataclass
class ArrayPush(Instr):
    array: Ref
    value: Ref


@dataclass
class ArrayExtend(Instr):
    array_loc: Loc
    item_ref: Ref


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
    value: Ref


@dataclass
class Pop(Instr):
    pass


Instr.get_children()
