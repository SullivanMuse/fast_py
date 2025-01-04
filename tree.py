# builtin
from comb import Span
from dataclasses import dataclass, field
from enum import auto, Enum
from typing import Optional


class Expr(Enum):
    # No free variables
    Int = auto()  # 123
    Tag = auto()  # :a
    Float = auto()  # 123.456
    String = auto()  # d"Hello\\, {x}"

    # Union of children
    Array = auto()  # [e0, e1, ...]
    Spread = auto()  # ...e0
    Paren = auto()  # (e0)
    Call = auto()  # e0(e1, e2, ...)
    Index = auto()  # e0[e1, e2, ...]
    Binary = auto()  # e0**e1
    Unary = auto()  # !e0 e0.await e0.chain e0? e0.x
    Comparison = auto()  # x is y isnot z

    # Special
    Id = auto()  # a
    Fn = auto()  # fn(p0, p1, ...) e0
    Block = auto()  # { s0, s1, ... }
    Match = auto()  # match e0 { arm... }
    Loop = auto()  # loop { ... }


class Pattern(Enum):
    Ignore = auto()  # _name

    Id = auto()  # a[@p]
    Tag = auto()  # :a
    Int = auto()  # 123
    Float = auto()  # 123.456
    String = auto()  # "Hello"

    Array = auto()  # [p0, ...p1, p2]
    Range = auto()  # [a]..[=][b]
    Gather = auto()  # ..r

    # TODO: {e0} dynamic literal pattern
    # TODO: p0 <- e0 Pattern guards


class Arm(Enum):
    Arm = auto()  # p0 -> e0


class Statement(Enum):
    Expr = auto()
    Let = auto()  # let p = e
    Assign = auto()  # p = e
    Loop = auto()  # loop { ... }
    Match = auto()  # match subject { arm... }
    Break = auto()  # break [x]
    Continue = auto()  # continue
    Return = auto()  # return [x]


@dataclass
class Node:
    span: Span = None
    ty: Expr | Statement | Pattern | Arm = None
    op: Optional[Span] = None
    children: list["Node"] = field(default_factory=list)

    # Tokens that are not syntax nodes, like { } ; ,
    tokens: list[Span] = field(default_factory=list)

    def pprint(self, depth=0, tokens=False):
        op_str = f" {self.op.string()}" if self.op else ""
        if self.span is None:
            print(
                f"{depth * '  '}{self.ty.name}{op_str}"
            )
        else:
            print(
                f"{depth * '  '}{self.ty.name}{op_str} {self.span.start}:{self.span.stop} {repr(self.span.str())}"
            )
        if tokens and self.tokens:
            print(
                f"{(depth + 1) * '  '}tokens = {' '.join(t.str() for t in self.tokens)}"
            )
        for child in self.children:
            if isinstance(child, Node):
                child.pprint(depth + 1)
            else:
                print(f"{(depth + 1) * '  '}Non-node child")

    def binds(self, set_=None) -> set[str]:
        if not isinstance(self.ty, Pattern):
            raise TypeError

        if set_ is None:
            set_ = set()

        match self.ty:
            case Pattern.Id:
                set_.add(self.span.str())
                raise NotImplementedError

            case _:
                raise NotImplementedError

        return set_

    def scope_free(self, set_=None, start_index=0) -> set[str]:
        scope = set()

        for child in self.children[start_index:]:
            match child.ty:
                case Statement.Let:
                    pat, expr = child.children
                    pat.binds(scope)
                    set_ += expr.free() - scope

                case Statement.Assign:
                    _pat, expr = child.children
                    expr.free(set_)

                case Statement.Loop:
                    child.scope_free(set_)

                case Statement.Match:
                    child.children[0].free(set_)
                    child.scope_free(set_, start_index=1)

                case Statement.Break | Statement.Continue | Statement.Return:
                    for child in self.children:
                        child.free(set_)

                case _:
                    raise NotImplementedError

        return set_

    def free(self, set_=None) -> set[str]:
        if not isinstance(self.ty, Expr):
            raise TypeError

        if set_ is None:
            set_ = set()

        match self.ty:
            # No free variables
            case Expr.Int | Expr.Tag | Expr.Float | Expr.String:
                pass

            # Union of children
            case Expr.Array | Expr.Spread | Expr.Paren | Expr.Call | Expr.Index | Expr.Binary | Expr.Unary | Expr.Comparison:
                for child in self.children:
                    child.free(set_)

            # Special
            case Expr.Id:
                set_.add(self.span.str())

            case Expr.Fn:
                patterns = []
                body = None
                for child in self.children:
                    if isinstance(child.ty, Pattern):
                        patterns.append(child)
                    else:
                        body = child
                body.free(set_)
                for pat in patterns:
                    pat.remove_free(set_)

            case Expr.Block:
                self.scope_free(set_)

            case Expr.Loop:
                self.scope_free(set_)

            case Expr.Match:
                self.children[0].free(set_)
                self.scope_free(set_, start_index=1)

        return set_
