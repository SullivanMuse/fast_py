from dataclasses import dataclass

from format_node import FormatNode


class ChildGetter:
    @classmethod
    def _get_classes(cls):
        for sub in cls.__subclasses__():
            setattr(cls, sub.__name__, sub)


class Ref(ChildGetter):
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


Ref._get_classes()


@dataclass
class Spread(FormatNode):
    value: Ref


@dataclass
class Instr(FormatNode, ChildGetter):
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
class Array(Instr):
    values: list[Ref | Spread]


@dataclass
class ArrayPush(Instr):
    array: Ref
    value: Ref


@dataclass
class ArrayExtend(Instr):
    array: Ref
    array_value: Ref


@dataclass
class Closure(Instr):
    spec: "ClosureSpec"


@dataclass
class Call(Instr):
    value: Ref


Instr._get_classes()
