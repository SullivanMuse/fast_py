from dataclasses import dataclass, field
from typing import Optional

from comb import Span
from mixins import FormatNode


@dataclass
class SyntaxNode(FormatNode):
    span: Span

    @property
    def children(self):
        raise NotImplementedError

    def str(self):
        return f"{self.ty.name} {self.span}"


@dataclass
class Expr(SyntaxNode):
    def free(self, set_=None) -> set[str]:
        if set_ is None:
            set_ = set()

        match self:
            case IdExpr(_, name, inner):
                set_.add(name.str())
                if inner is not None:
                    inner.free(set_)

            case FnExpr(_, _, inner):
                patterns = []
                body = None
                for child in self.children:
                    if isinstance(child, Pattern):
                        patterns.append(child)
                    else:
                        body = child
                body.free(set_)
                for pat in patterns:
                    pat.remove_bound(set_)

            case LoopExpr(_, statements):
                free(statements, set_)

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
                for child in self.children:
                    child.free(set_)

            case IntExpr(_) | TagExpr(_) | FloatExpr(_) | StringExpr(_):
                pass

            case _:
                raise NotImplementedError(f"`{type(self)}.free`")

        return set_


@dataclass
class IntExpr(Expr):
    """Integer literal expression

    Example:
        123
    """

    pass


@dataclass
class TagExpr(Expr):
    """Tag literal expression

    Example:
        :a
    """

    pass


@dataclass
class FloatExpr(Expr):
    """Float literal expression

    Example:
        123.456
    """

    pass


@dataclass
class StringExpr(Expr):
    """String literal expression

    Example:
        d"Hello\\, {x}"
    """

    fn: Optional[Span]

    # >= 1
    chars: list[str]

    # len = len(chars) - 1
    interpolants: list[Expr]

    lquote: Span
    rquote: Span


@dataclass
class ArrayExpr(Expr):
    """Array literal expression

    Example:
        [e0, e1, ...]
    """

    lbracket: Span
    items: list[Expr]
    rbracket: Span


@dataclass
class Spread(Expr):
    """Spread operator pseudo-expression

    May only appear within an array literal expression or a struct literal expression

    Example:
        ...e0
    """

    ellipsis: Span
    inner: Expr


@dataclass
class ParenExpr(Expr):
    """Parenthesized expression

    Example:
        (e0)
    """

    lpar: Span
    inner: Expr
    rpar: Span


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


@dataclass
class BinaryExpr(Expr):
    """Binary operator expression

    Example:
        e0**e1
    """

    pass


@dataclass
class UnaryExpr(Expr):
    """Unary operator expression

    Example:
        !e0 e0.await e0.chain e0? e0.x
    """

    pass


@dataclass
class ComparisonExpr(Expr):
    """Comparison expression

    Example:
        x is y isnot z
    """

    pass


@dataclass
class IdExpr(Expr):
    """Identifier

    Example:
        a
    """

    pass


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


@dataclass
class BlockExpr(Expr):
    """Block expression

    Example:
        { s0, s1, ... }
    """

    lbrace: Span
    statements: list["Statement"]
    rbrace: Span


@dataclass
class Arm(SyntaxNode):
    pattern: "Pattern"
    arrow_token: Span
    expr: Expr


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


def free(statements, set_=None) -> set[str]:
    if set_ is None:
        set_ = set()
    scope = set()
    for statement in statements:
        match statement:
            case ExprStatement(_, inner):
                inner.free(set_)

            case LetStatement(_, pattern, inner):
                pattern.binds(scope)
                set_ += inner.free() - scope

            case AssignStatement(_, pattern, inner):
                set_ += inner.free() - scope

            case LoopStatement(_, statements):
                free(statements, set_)

            case MatchStatement(_, subject, arms):
                subject.free(set_)
                for pattern, expr in arms:
                    set_ += expr.free() - pattern.bind() - scope

            case BreakStatement(_, _, expr):
                if expr is not None:
                    expr.free(set_)

            case ContinueStatement(_, _):
                pass

            case ReturnStatement(_, inner):
                inner.free(set_)

            case _:
                raise NotImplementedError(f"`{type(statement)}.free`")
    return set_


@dataclass
class Statement(SyntaxNode):
    semi_token: Optional[Span]


@dataclass
class ExprStatement(Statement):
    """

    Example:
        e
    """

    inner: Expr


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


@dataclass
class LetStatement(Statement):
    """

    Example:
        let p = e
    """

    pattern: "Pattern"
    inner: Expr

    # tokens
    let_token: Span
    eq_token: Span


@dataclass
class AssignStatement(Statement):
    """

    Example:
        p = e
    """

    pattern: "Pattern"
    inner: Expr

    eq_token: Span


@dataclass
class LoopStatement(Statement):
    """

    Example:
        loop { ... }
    """

    loop_expr: LoopExpr


@dataclass
class MatchStatement(Statement):
    """

    Example:
        match subject { arm... }
    """

    match_expr: MatchExpr


@dataclass
class BreakStatement(Statement):
    """

    Example:
        break ['label] [e]
    """

    break_token: Span
    label: Optional[Span]
    inner: Optional[Expr]


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


@dataclass
class ReturnStatement(Statement):
    """

    Example:
        return [x]
    """

    return_token: Span
    inner: Optional[Expr]


@dataclass
class Pattern(SyntaxNode):
    def bind(self, set_=None) -> set[str]:
        if set_ is None:
            set_ = set()
        match self:
            case IdPattern(_, name, inner):
                set_.add(name.str())
                inner.bind(set_)

            case ArrayPattern(_, items, _, _, _):
                for item in items:
                    item.bind(set_)

            case GatherPattern(_, _, inner):
                inner.bind(set_)

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
        return set_


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


@dataclass
class GatherPattern(Pattern):
    """A pseudo-pattern that gathers remaining elements in an array or struct

    May only appear within an `ArrayPattern`

    Example:
        ...p
    """

    ellipsis: Span
    inner: Pattern
