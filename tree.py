# builtin
from comb import Span
from dataclasses import dataclass, field
from enum import auto, Enum
from typing import Optional

# project
from format_node import FormatNode


class ExprTy(Enum):
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


class PatternTy(Enum):
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


class StatementTy(Enum):
    Expr = auto()
    Let = auto()  # let p = e
    Assign = auto()  # p = e
    Loop = auto()  # loop { ... }
    Match = auto()  # match subject { arm... }
    Break = auto()  # break [x]
    Continue = auto()  # continue
    Return = auto()  # return [x]


@dataclass
class SyntaxNode(FormatNode):
    span: Span
    ty: ExprTy | StatementTy | PatternTy
    children: list["SyntaxNode"] = field(default_factory=list)
    op: Optional[Span] = None

    # Tokens that are not syntax nodes, like { } ; ,
    tokens: list[Span] = field(default_factory=list)

    def str(self):
        return f"{self.ty.name} {self.span}"


@dataclass
class Expr(SyntaxNode):
    def free(self, set_=None) -> set[str]:
        if not isinstance(self.ty, ExprTy):
            raise TypeError

        if set_ is None:
            set_ = set()

        match self.ty:
            # No free variables
            case ExprTy.Int | ExprTy.Tag | ExprTy.Float | ExprTy.String:
                pass

            # Union of children
            case ExprTy.Array | ExprTy.Spread | ExprTy.Paren | ExprTy.Call | ExprTy.Index | ExprTy.Binary | ExprTy.Unary | ExprTy.Comparison:
                for child in self.children:
                    child.free(set_)

            # Special
            case ExprTy.Id:
                set_.add(self.span.str())

            case ExprTy.Fn:
                patterns = []
                body = None
                for child in self.children:
                    if isinstance(child.ty, PatternTy):
                        patterns.append(child)
                    else:
                        body = child
                body.free(set_)
                for pat in patterns:
                    pat.remove_free(set_)

            case ExprTy.Block:
                self.scope_free(set_)

            case ExprTy.Loop:
                self.scope_free(set_)

            case ExprTy.Match:
                self.children[0].free(set_)
                self.scope_free(set_, start_index=1)

        return set_


@dataclass
class Statement(SyntaxNode):
    def scope_free(self, set_=None, start_index=0) -> set[str]:
        scope = set()

        for child in self.children[start_index:]:
            match child.ty:
                case StatementTy.Let:
                    pat, expr = child.children
                    pat.binds(scope)
                    set_ += expr.free() - scope

                case StatementTy.Assign:
                    _pat, expr = child.children
                    expr.free(set_)

                case StatementTy.Loop:
                    child.scope_free(set_)

                case StatementTy.Match:
                    child.children[0].free(set_)
                    child.scope_free(set_, start_index=1)

                case StatementTy.Break | StatementTy.Continue | StatementTy.Return:
                    for child in self.children:
                        child.free(set_)

                case _:
                    raise NotImplementedError

        return set_


@dataclass
class Pattern(SyntaxNode):
    def binds(self, set_=None) -> set[str]:
        if not isinstance(self.ty, PatternTy):
            raise TypeError

        if set_ is None:
            set_ = set()

        match self.ty:
            case PatternTy.Id:
                set_.add(self.span.str())
                raise NotImplementedError

            case _:
                raise NotImplementedError

        return set_
