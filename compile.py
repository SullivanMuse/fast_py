from dataclasses import dataclass, field
from typing import Optional

from errors import CompileError
from instr import ArrayExtend, ArrayPush, Assert, Call, ClosureNew, Jump, Loc, Pop, Push, Ref
from parse import statements
from tree import (
    ArrayExpr,
    BinaryExpr,
    BlockExpr,
    CallExpr,
    ComparisonExpr,
    Expr,
    ExprStatement,
    FloatExpr,
    FnExpr,
    IdExpr,
    IndexExpr,
    IntExpr,
    LetStatement,
    LoopExpr,
    MatchExpr,
    ParenExpr,
    Pattern,
    Spread,
    Statement,
    StringExpr,
    SyntaxNode,
    TagExpr,
    UnaryExpr,
)
from value import *


@dataclass
class Scope:
    prev: Optional["Scope"] = None
    map: dict[str, Loc] = field(default_factory=dict)
    temporary_count: int = 0

    def __getitem__(self, key) -> Loc:
        try:
            return self.map[key]
        except KeyError:
            if self.prev is None:
                raise KeyError
            return self.prev[key]

    def __setitem__(self, key, value):
        self.map[key] = value

    def temporary(self) -> Loc:
        ix = len(self.map) + self.temporary_count
        self.temporary_count += 1
        return Loc(ix)

    def pop(self):
        """Reduce temporaries"""
        self.temporary_count -= 1


@dataclass
class Compiler:
    scope: Scope = field(default_factory=Scope)
    code: list[SyntaxNode] = field(default_factory=list)

    def push(self, instr: Instr) -> Optional[Loc]:
        """Push the instruction into the code object

        Args:
            instr (Instr): The instruction to push

        Raises:
            NotImplementedError: The instruction type is not implemented

        Returns:
            Optional[Loc]: The location of the value pushed on the stack by the instruction, if any
        """
        self.code.append(instr)

        ix = None
        match instr:
            case Push(ref):
                ix = self.scope.temporary()

            case ArrayPush(ref):
                self.scope.pop()

            case ArrayExtend(array_loc, item_ref):
                pass

            case ClosureNew(spec):
                ix = self.scope.temporary()

            case Call(ref):
                ix = self.scope.temporary()

            case Jump(condition, dest):
                pass

            case Pop():
                self.scope.pop()

            case _:
                raise NotImplementedError(f"`Compiler.push({type(instr).__name__})`")

        return ix

    def compile_pattern(self, pattern: Pattern) -> Loc:
        """Attempts to match the value on the top of the stack

        Args:
            pattern (Pattern): The pattern to match

        Raises:
            NotImplementedError: The given pattern type is not implemented

        Returns:
            int: The stack location of the boolean value indicating whether the pattern matched or not
        """
        match pattern:
            case _:
                raise NotImplementedError(f"Compiler.compile_pattern({type(pattern).__name__})")

    def compile_statement(self, statement: Statement) -> Optional[Loc]:
        """Compile the statement

        Args:
            statement (Statement): The statement to compile

        Raises:
            NotImplementedError: The statement type is not implemented

        Returns:
            Optional[Loc]: The location of the value produced by the statement
        """
        match statement:
            case ExprStatement(_, inner):
                return self.compile_expr(inner)

            case LetStatement(pattern, inner):
                self.compile_expr(inner)
                ix = self.compile_pattern(pattern)
                return self.push(Assert(Loc(ix), "irrefutable bind failure"))

            case _:
                raise NotImplementedError(
                    f"`Compiler.compile_statement({type(statement).__name__})`"
                )

    def compile_statements(self, statements: list[Statement]) -> Optional[Loc]:
        """Compile a series of statements

        Args:
            statements (list[Statement]): The statements to compile

        Returns:
            Optional[Loc]: The location of the value created by the final statement, if any
        """
        self.scope = Scope(self.scope)
        result = None
        for statement in statements:
            result = self.compile_statement(statement)
        if result is None:
            instr = Push(Ref.Imm(Unit()))
            result = self.push(instr)
        self.scope = self.scope.prev
        return result

    def compile_expr(self, expr: Expr) -> Loc:
        """Compile the expression

        Args:
            expr (Expr): The expression to compile

        Raises:
            CompileError: Spread expression appears outside of an array literal
            NotImplementedError: The expression type is not implemented

        Returns:
            Loc: The location of the value produced by the expression
        """
        match expr:
            case IdExpr(span):
                name = span.str()
                item_loc = self.scope[name]
                instr = Push(item_loc)
                return self.push(instr)

            case IntExpr(span):
                value = Int(int(span.str()))
                instr = Push(Ref.Imm(value))
                return self.push(instr)

            case TagExpr(_, name):
                value = Tag(name.str())
                instr = Push(Ref.Imm(value))
                return self.push(instr)

            case FloatExpr(span):
                value = Float(float(span.str()))
                instr = Push(Ref.Imm(value))
                return self.push(instr)

            case StringExpr(_, fn, items, _, _):
                raise NotImplementedError

            case ArrayExpr(span, _, items, _):
                instr = Push(Array([None * len(items)]))
                array_loc = self.push(instr)
                for item in items:
                    match item:
                        case Spread(span, ellipsis, inner):
                            item_loc = self.compile_expr(item)
                            instr = ArrayExtend(array_loc, item_loc)

                        case _:
                            item_loc = self.compile_expr(item)
                            instr = ArrayPush(array_loc, item_loc)
                    self.push(instr)
                return array_loc

            case Spread(_, _, _):
                raise CompileError("Spread expression outside of array literal")

            case ParenExpr(_, inner):
                return self.compile_expr(inner)

            case FnExpr(span, params, inner):
                # Compute free variables
                free = inner.free()

                # Collect indices of captured variables
                captures = {}
                for k in free:
                    captures[k] = self.scope[free]

                # Create new scope for function and allocate space for captured variables
                scope = Scope()
                item_ix = 0
                for k in free:
                    scope[k] = item_ix
                    item_ix += 1

                # Allocate space for function arguments
                args, body = expr.children
                for arg in args:
                    scope[arg] = item_ix
                    item_ix += 1

                # Compile the function
                new_compiler = Compiler(scope)
                result_ix = new_compiler.compile(body)
                spec = ClosureSpec(new_compiler.code, len(args), captures.values())

                return self.push(ClosureNew(spec))

            case BlockExpr(span, statements):
                return self.compile_statements(statements)

            case MatchExpr(span, subject, arms):
                raise NotImplementedError

            case LoopExpr(span, statements):
                raise NotImplementedError

            case CallExpr(span):
                raise NotImplementedError

            case IndexExpr(span):
                raise NotImplementedError

            case BinaryExpr(span):
                raise NotImplementedError

            case UnaryExpr(span):
                raise NotImplementedError

            case ComparisonExpr(span):
                raise NotImplementedError

            case _:
                raise NotImplementedError(f"`Compiler.compile({type(expr).__name__})`")

    def into_closure(self) -> Closure:
        """Turn the code object from the compiler into a Closure and clear the compiler

        Returns:
            Closure: The closure produced from the code object
        """
        closure = Closure(ClosureSpec(self.code, 0, []), [])
        self.scope = Scope()
        self.code = []
        return closure


def compile(input: Expr | list[Statement] | str):
    compiler = Compiler()
    if isinstance(input, str):
        res = statements(input)
        compiler.compile_statements(res.val)
    elif isinstance(input, Expr):
        compiler.compile_expr(input)
    elif isinstance(input, list):
        compiler.compile_statements(input)
    else:
        raise TypeError

    return compiler.into_closure()
