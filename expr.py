from typing import Optional
from comb import Span
from dataclasses import dataclass

@dataclass
class Statement:
    span: Span

@dataclass
class Expr(Statement):
    pass

@dataclass
class Integer(Expr):
    pass

@dataclass
class Float(Expr):
    pass

@dataclass
class String(Expr):
    op: "Id"
    pieces: list[str]
    interpolants: list[Expr]

@dataclass
class Array(Expr):
    inner: Expr

@dataclass
class Range(Expr):
    left: Optional[Expr]
    right: Optional[Expr]
    type: str # closed or clopen

@dataclass
class Paren(Expr):
    inner: Expr

@dataclass
class Id(Expr):
    pass

@dataclass
class TruePostfix(Expr):
    # await, chain, or ?
    op: str

@dataclass
class BinOp(Expr):
    # One of
    #   ** * @ / // /^ % + - << >> & ^ | and or
    op: str
    left: Expr
    right: Expr

@dataclass
class MixFix(BinOp):
    # op is one of
    #   call, index, or `method`
    method_name: Optional[str]

@dataclass
class Comparison(Expr):
    # Invariant: len(inner) == len(comparators) + 1
    # Each comparator is one of
    #   in notin is isnot < <= > >= == !=
    comparators: list[str]
    inner: list[Expr]

@dataclass
class Tuple(Expr):
    inner: list[Expr]

@dataclass
class If(Expr):
    # Invariant: len(blocks) is equal or one greater than len(predicates)
    predicates: list[Expr]
    blocks: list[Expr]

@dataclass
class Return(Expr):
    """May only appear within a lambda or function declaration"""
    inner: Optional[Expr]

@dataclass
class Break(Expr):
    """May only appear within a loop"""
    pass

@dataclass
class Continue(Expr):
    """May only appear within a loop"""
    pass

@dataclass
class For(Statement):
    variable: Id
    quantifier: Expr
    body: Expr

@dataclass
class While(Statement):
    condition: Expr
    body: Expr

@dataclass
class Loop(Statement):
    body: Expr

@dataclass
class Mutation:
    pattern: Id
    expression: Expr

@dataclass
class Assignment:
    pattern: Id
    expression: Expr

@dataclass
class Module(Statement):
    name: Optional[str]
    contents: list[Statement]

@dataclass
class PathList:
    paths: list["Path"]

@dataclass
class As:
    name: str
    new_name: str

@dataclass
class Path:
    pre: list[str]
    terminal: As | PathList

@dataclass
class Use:
    path: Path
