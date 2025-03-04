from dataclasses import dataclass, field
from typing import Optional

from comb import Span
from mixins import FormatNode, GetChildren


def free(statements: list["Statement"]):
    """Iterate over free variables in statements"""
    bound = set()
    for statement in statements:
        bound.update(statement.early_bound())
    for statement in statements:
        for var in statement.free():
            if var not in bound:
                yield var
        bound.update(statement.bound())


MAX_DEPTH = 10


@dataclass
class SyntaxNode(FormatNode):
    span: Span

    def short(self):
        return f"{type(self).__name__} {self.span}"


@dataclass
class Expr(SyntaxNode, GetChildren):
    def free(self):
        match self:
            case IdExpr():
                yield self.span.str()

            case FnExpr():
                bound = set()
                for pat in self.params:
                    bound.update(pat.bound())
                for var in self.inner.free():
                    if var not in bound:
                        yield var

            case LoopExpr():
                yield from free(self.statements)

            case StringExpr():
                for child in self.children():
                    yield from child.free()

            case (
                ArrayExpr(_)
                | Spread(_)
                | ParenExpr(_)
                | CallExpr(_)
                | IndexExpr(_)
                | BinaryExpr(_)
                | UnaryExpr(_)
                | ComparisonExpr(_)
            ):
                for child in self.children():
                    yield from child.free()

            case IntExpr(_) | TagExpr(_) | FloatExpr(_) | StringExpr(_):
                pass

            case BlockExpr():
                yield from free(self.statements)

            case MatchExpr():
                yield from self.subject.free()
                for pat, expr in self.arms:
                    bound = pat.bound()
                    for var in expr.free():
                        if var not in bound:
                            yield var

            case _:
                raise NotImplementedError(f"`{type(self)}.free`")

        return free


@dataclass
class IntExpr(Expr):
    """Integer literal expression

    Example:
        123
    """


@dataclass
class TagExpr(Expr):
    """Tag literal expression

    Example:
        :a
    """


@dataclass
class FloatExpr(Expr):
    """Float literal expression

    Example:
        123.456
    """


@dataclass
class StringExpr(Expr):
    """String literal expression

    Example:
        d"Hello\\, {x}"
    """

    fn: Optional["IdExpr"]

    # >= 1
    chars: list[str]

    # len = len(chars) - 1
    interpolants: list[Expr]

    lquote: Span
    rquote: Span

    def children(self):
        if self.fn is not None:
            yield self.fn
        yield from self.interpolants


@dataclass
class ArrayExpr(Expr):
    """Array literal expression

    Example:
        [e0, e1, ...]
    """

    lbracket: Span
    items: list[Expr]
    rbracket: Span

    def children(self):
        yield from self.items


@dataclass
class Spread(Expr):
    """Spread operator pseudo-expression

    May only appear within an array literal expression or a struct literal expression

    Example:
        ...e0
    """

    ellipsis: Span
    inner: Expr

    def children(self):
        yield self.inner


@dataclass
class ParenExpr(Expr):
    """Parenthesized expression

    Example:
        (e0)
    """

    lpar: Span
    inner: Expr
    rpar: Span

    def children(self):
        yield self.inner


@dataclass
class CallExpr(Expr):
    """Call expression

    Example:
        e0(e1, e2, ...)
    """

    fn: Expr
    lpar_token: Span
    args: list[Expr]
    rpar_token: Span

    def children(self):
        yield self.fn
        yield from self.args


@dataclass
class IndexExpr(Expr):
    """Index expression

    Example:
        e0[e1, e2, ...]
    """

    subject: Expr
    lsq_token: Span
    indices: list[Expr]
    rsq_token: Span

    def children(self):
        yield self.subject
        yield from self.indices


@dataclass
class BinaryExpr(Expr):
    """Binary operator expression

    Example:
        e0**e1
    """

    op: Span
    left: Expr
    right: Expr

    def children(self):
        yield self.left
        yield self.right


@dataclass
class UnaryExpr(Expr):
    """Unary operator expression

    Example:
        !e0 e0.await e0.chain e0? e0.x
    """

    op: Span
    inner: Expr

    def children(self):
        yield self.inner


@dataclass
class ComparisonExpr(Expr):
    """Comparison expression

    Example:
        x is y isnot z
    """

    ops: list[Span]  # len(self.ops) == len(self.inner) - 1
    inner: list[Expr]

    def children(self):
        yield from self.inner


@dataclass
class IdExpr(Expr):
    """Identifier

    Example:
        a
    """


@dataclass
class FnExpr(Expr):
    """Function expression

    Example:
        fn(p0, p1, ...) e0
    """

    fn_token: Span
    lpar: Span
    params: list["Pattern"]
    rpar: Span
    inner: Expr

    def children(self):
        yield from self.params
        yield self.inner


@dataclass
class BlockExpr(Expr):
    """Block expression

    Example:
        { s0, s1, ... }
    """

    lbrace: Span
    statements: list["Statement"]
    rbrace: Span

    def children(self):
        yield from self.statements


@dataclass
class Arm(SyntaxNode):
    pattern: "Pattern"
    arrow_token: Span
    expr: Expr

    def children(self):
        yield self.pattern
        yield self.expr


@dataclass
class MatchExpr(Expr):
    """Match expression

    Example:
        match e0 { arm... }
    """

    match_token: Span
    subject: Expr
    lbrace_token: Span
    arms: list[Arm]
    rbrace_token: Span

    def children(self):
        yield self.subject
        yield from self.arms


@dataclass
class LoopExpr(Expr):
    """Loop expression

    Example:
        loop { ... }
    """

    loop_token: Span
    lbrace_token: Span
    statements: list["Statement"]
    rbrace_token: Span

    def children(self):
        yield from self.statements


@dataclass
class Statement(SyntaxNode, GetChildren):
    semi_token: Optional[Span]

    def free(self):
        """Iterate over free variables in statement"""

        match self:
            case ExprStatement():
                yield from self.inner.free()

            case LetStatement():
                yield from self.inner.free()

            case AssignStatement():
                yield from self.pattern.free()
                yield from self.inner.free()

            case LoopStatement():
                yield from free(self.statements)

            case MatchStatement():
                yield from self.match_expr.free()

            case BreakStatement():
                if self.expr is not None:
                    yield from self.expr.free()

            case ContinueStatement():
                pass

            case ReturnStatement():
                yield from self.inner.free()

            case FnStatement():
                bound = set()
                bound.add(self.name.str())
                for pat in self.params:
                    bound.update(pat.bound())
                    for var in free(self.body):
                        if var not in bound:
                            yield var

            case _:
                raise NotImplementedError(f"`{type(self)}.free`")

    def early_bound(self):
        match self:
            case FnStatement():
                yield self.name.str()

    def bound(self):
        match self:
            case LetStatement():
                yield from self.pattern.bound()


@dataclass
class ExprStatement(Statement):
    """

    Example:
        e
    """

    inner: Expr

    def children(self):
        yield self.inner


@dataclass
class FnStatement(Statement):
    fn_token: Span
    name: Span

    lpar_token: Span
    params: list["Pattern"]
    rpar_token: Span

    lbrace_token: Span
    body: list[Statement]
    rbrace_token: Span

    def children(self):
        yield from self.params
        yield from self.body


@dataclass
class LetStatement(Statement):
    """

    Example:
        let p = e
    """

    let_token: Span
    pattern: "Pattern"
    eq_token: Span
    inner: Expr

    def children(self):
        yield self.pattern
        yield self.inner


@dataclass
class AssignStatement(Statement):
    """

    Example:
        p = e
    """

    pattern: "Pattern"
    eq_token: Span
    inner: Expr

    def children(self):
        yield self.pattern
        yield self.inner


@dataclass
class LoopStatement(Statement):
    """

    Example:
        loop { ... }
    """

    loop_expr: LoopExpr

    def children(self):
        yield self.loop_expr


@dataclass
class MatchStatement(Statement):
    """

    Example:
        match subject { arm... }
    """

    match_expr: MatchExpr

    def children(self):
        yield self.match_expr


@dataclass
class BreakStatement(Statement):
    """

    Example:
        break ['label] [e]
    """

    break_token: Span
    label: Optional[Span]
    inner: Optional[Expr]

    def children(self):
        if self.inner is not None:
            yield self.inner


@dataclass
class ContinueStatement(Statement):
    """

    Example:
        continue ['label]
    """

    continue_token: Span
    label: Optional[Span]


@dataclass
class BlockStatement(Statement):
    """Block statement

    Example:
        { s0, s1, ... }
    """

    statements: list["Statement"]

    def children(self):
        yield from self.statements


@dataclass
class ReturnStatement(Statement):
    """

    Example:
        return [x]
    """

    return_token: Span
    inner: Optional[Expr]

    def children(self):
        if self.inner is not None:
            yield self.inner


@dataclass
class Pattern(SyntaxNode, GetChildren):
    def free(self):
        """Iterate over free variables"""

        yield from ()

    def bound(self):
        """Iterate over bound variables"""

        match self:
            case IdPattern():
                yield self.name.str()
                if self.inner is not None:
                    yield from self.inner.bound()

            case ArrayPattern():
                for item in self.items:
                    yield from item.bound()

            case GatherPattern():
                yield from self.inner.bound()

            case (
                IgnorePattern(_)
                | TagPattern(_)
                | IntPattern(_)
                | FloatPattern(_)
                | StringPattern(_)
            ):
                pass

            case _:
                raise NotImplementedError(f"`{type(self)}.bind`")


@dataclass
class IgnorePattern(Pattern):
    """A pattern that matches anything

    Example:
        _name
    """

    pass


@dataclass
class IdPattern(Pattern):
    """A pattern that matches anything, or whatever the inner pattern matches, and then binds the matched value to a new name

    Example:
        a[@p]
    """

    name: Span
    at_token: Optional[Span] = None
    inner: Optional[Pattern] = None

    def children(self):
        if self.inner is not None:
            yield self.inner


@dataclass
class TagPattern(Pattern):
    """A pattern that matches a tag

    Example:
        :a
    """

    pass


@dataclass
class IntPattern(Pattern):
    """A pattern that matches an integer

    Example:
        123
    """

    pass


@dataclass
class FloatPattern(Pattern):
    """A pattern that matches a float value

    Example:
        123.456
    """

    pass


@dataclass
class StringPattern(Pattern):
    """A pattern that matches a string

    Example:
        "Hello"
    """

    lquote_token: Span
    piece: Span
    rquote_token: Span


@dataclass
class ArrayPattern(Pattern):
    """A pattern that matches an array

    Example:
        [p0, ...p1, p2]
    """

    items: list[Pattern]
    lsq: Span
    commas: list[Span]
    rsq: Span

    def children(self):
        yield from self.items


@dataclass
class GatherPattern(Pattern):
    """A pseudo-pattern that gathers remaining elements in an array or struct

    May only appear within an `ArrayPattern`

    Example:
        ...p
    """

    ellipsis: Span
    inner: Pattern

    def children(self):
        yield self.inner


Expr.get_children()
Pattern.get_children()
Statement.get_children()
