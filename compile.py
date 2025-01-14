from dataclasses import dataclass, field
from typing import Optional

from errors import CompileError
from instr import (ArrayExtend, ArrayPush, Call, ClosureNew, Jump, Loc, Pop,
                   Push, Ref)
from tree import (ArrayExpr, BinaryExpr, BlockExpr, CallExpr, ComparisonExpr,
                  Expr, ExprStatement, FloatExpr, FnExpr, IdExpr, IndexExpr,
                  IntExpr, LoopExpr, MatchExpr, ParenExpr, Spread, Statement,
                  StringExpr, SyntaxNode, TagExpr, UnaryExpr)
from value import *


@dataclass
class Scope:
    prev: Optional["Scope"] = None
    map: dict[str, int] = field(default_factory=dict)
    temporary_count: int = 0

    def __getitem__(self, key) -> Loc:
        try:
            return Loc(self.map[key])
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

    def push(self, code: SyntaxNode) -> Optional[Loc]:
        self.code.append(code)

        ix = None
        match code.ty:
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
                raise NotImplementedError(f"`Compiler.push({type(code).__name__})`")

        return ix

    def compile_statement(self, statement: Statement) -> Optional[int]:
        match statement:
            case ExprStatement(_, inner):
                return self.compile_expr(inner)

            case _:
                raise NotImplementedError(f"`Compiler.compile_statement({type(statement).__name__})`")

    def compile_statements(self, statements: list[Statement]) -> int:
        self.scope = Scope(self.scope)
        result_ix = None
        for statement in statements:
            result_ix = self.compile_statement(statement)
        if result_ix is None:
            instr = Push(Ref.Imm(Unit()))
            result_ix = self.push(instr)
        self.scope = self.scope.prev
        return result_ix

    def compile_expr(self, expr: Expr) -> int:
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
