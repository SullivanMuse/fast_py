from comb import Span
from dataclasses import dataclass, field
from enum import auto, Enum
from typing import Optional


class Expr(Enum):
    Id = auto() # a
    Int = auto() # 123
    Tag = auto() # :a
    Float = auto() # 123.456
    String = auto() # d"Hello\\, {x}"
    Array = auto() # [e0, e1, ...]
    Spread = auto() # ...e0
    Paren = auto() # (e0)
    Fn = auto() # fn(p0, p1, ...) e0
    Block = auto() # { s0, s1, ... }
    Match = auto() # match e0 { arm... }
    Loop = auto() # loop { ... }
    Call = auto() # e0(e1, e2, ...)
    Index = auto() # e0[e1, e2, ...]
    Binary = auto() # e0**e1
    Unary = auto() # !e0 e0.await e0.chain e0? e0.x
    Comparison = auto() # x is y isnot z


class Pattern(Enum):
    Ignore = auto() # _name
    Id = auto() # a[@p]
    Tag = auto() # :a
    Int = auto() # 123
    Float = auto() # 123.456
    String = auto() # "Hello"
    Array = auto() # [p0, ...p1, p2]
    Range = auto() # [a]..[=][b]
    Gather = auto() # ..r
    # {e0} dynamic literal pattern
    # p0 <- e0 Pattern guards


class Arm(Enum):
    Arm = auto() # p0 -> e0


class Statement(Enum):
    Let = auto() # let p = e
    Assign = auto() # p = e
    Loop = auto() # loop { ... }
    Match = auto() # match subject { arm... }
    Break = auto() # break [x]
    Continue = auto() # continue
    Return = auto() # return [x]


@dataclass
class Node:
    span: Span
    ty: Expr | Statement | Pattern | Arm
    op: Optional[Span] = None
    children: list["Node"] = field(default_factory=list)

    # Tokens that are not syntax nodes, like { } ; ,
    tokens: list[Span] = field(default_factory=list)

    @property
    def left(self):
        if len(self.children) != 2:
            raise ValueError
        return self.children[0]

    @property
    def right(self):
        if len(self.children) != 2:
            raise ValueError
        return self.children[0]

    def pprint(self, depth=0, tokens=False):
        op_str = f" {self.op.string()}" if self.op else ""
        print(f"{depth * '  '}{self.ty.name}{op_str} {self.span.start}:{self.span.stop} {repr(self.span.str())}")
        if tokens and self.tokens:
            print(f"{(depth + 1) * '  '}tokens = {' '.join(t.string() for t in self.tokens)}")
        for child in self.children:
            if isinstance(child, Node):
                child.pprint(depth + 1)
            else:
                print(f"{(depth + 1) * '  '}Non-node child")
