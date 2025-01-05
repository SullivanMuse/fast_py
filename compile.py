from dataclasses import dataclass, field
from typing import Optional

from comb import Span
from vm.instr import Imm, Instr, InstrTy
from tree import Expr, ExprTy, Statement, SyntaxNode, StatementTy
from vm.value import ClosureSpec, Value, ValueTy


@dataclass
class Scope:
    prev: Optional["Scope"] = None
    map: dict[str, int] = field(default_factory=dict)
    temporary_count: int = 0

    def __getitem__(self, key) -> int:
        try:
            return self.map[key]
        except KeyError:
            if self.prev is None:
                raise KeyError
            return self.prev[key]

    def __setitem__(self, key, value):
        self.map[key] = value

    def temporary(self) -> int:
        ix = len(self.map) + self.temporary_count
        self.temporary_count += 1
        return ix


@dataclass(frozen=True)
class CompileError(Exception):
    span: Span
    reason: str


@dataclass
class Compiler:
    scope: Scope = field(default_factory=Scope)
    code: list[SyntaxNode] = field(default_factory=list)

    def push(self, code: SyntaxNode) -> int:
        self.code.append(code)
        match code.ty:
            case InstrTy.Push:
                ix = self.scope.temporary()

            case InstrTy.Call:
                ix = self.scope.temporary()

            case InstrTy.Array:
                ix = self.scope.temporary()

            case InstrTy.ArrayPush:
                ix = None

            case _:
                raise NotImplementedError

        return ix

    def compile(self, statements: list[Statement]):
        for statement in statements:
            self.compile_statement(statement)

    def compile_statement(self, statement: Statement) -> Optional[int]:
        match statement.ty:
            case StatementTy.Expr:
                return self.compile_expr(statement.children[0])

            case _:
                raise NotImplementedError

    def compile_scope(self, statements: list[Statement]) -> int:
        self.scope = Scope(self.scope)
        result_ix = None
        for statement in statements:
            result_ix = self.compile_statement(statement)
        if result_ix is None:
            instr = Instr(InstrTy.Push, [Imm(Value(ValueTy.Unit))])
            result_ix = self.push(instr)
        self.scope = self.scope.prev
        return result_ix

    def compile_expr(self, expr: Expr) -> int:
        match expr.ty:
            case ExprTy.Id:
                id = expr.span.str()
                item_ix = self.scope[id]
                instr = Instr(InstrTy.Local, [item_ix])
                return self.push(instr)

            case ExprTy.Int:
                value = Value(ValueTy.Int, [int(expr.span.str())])
                instr = Instr(ty=InstrTy.Push, children=[value])
                return self.push(instr)

            case ExprTy.Tag:
                value = Value(ValueTy.Tag, [expr.span.str()])
                instr = Instr(InstrTy.Push, [value])
                return self.push(instr)

            case ExprTy.Float:
                value = Value(ValueTy.Float, [float(expr.span.str())])
                instr = Instr(InstrTy.Push, [value])
                return self.push(instr)

            case ExprTy.String:
                raise NotImplementedError

            case ExprTy.Array:
                length = Imm(Value(ValueTy.Int, len(expr.children)))
                instr = Instr(InstrTy.Array, [length])
                array_ix = Imm(Value(ValueTy.Int, [self.push(instr)]))
                for child in expr.children:
                    if child.ty == ExprTy.Spread:
                        item_ix = Imm(
                            Value(ValueTy.Int, [self.compile_expr(child.child)])
                        )
                        instr = Instr(InstrTy.ArrayExtend, [array_ix, item_ix])
                    else:
                        item_ix = Imm(Value(ValueTy.Int, [self.compile_expr(child)]))
                        instr = Instr(InstrTy.ArrayPush, [array_ix, item_ix])
                    self.push(instr)
                return array_ix

            case ExprTy.Spread:
                raise CompileError("Spread expression outside of array literal")

            case ExprTy.Paren:
                return self.compile_expr(expr.children[0])

            case ExprTy.Fn:
                # Compute free variables
                free = expr.free()

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

                return self.push(Instr(InstrTy.Closure, [spec]))

            case ExprTy.Block:
                return self.compile_scope(expr.children)

            case ExprTy.Match:
                raise NotImplementedError

            case ExprTy.Loop:
                raise NotImplementedError

            case ExprTy.Call:
                fn_ix = self.compile_expr(expr.children[0])
                args_ix = []
                for child in expr.children[1:]:
                    args_ix.append(self.compile_expr(child))
                for arg_ix in args_ix:
                    self.push(Instr(InstrTy.Push, [Imm(Value(ValueTy.Int, [arg_ix]))]))
                return self.push(Instr(InstrTy.Call, [Imm(Value(ValueTy.Int, [fn_ix]))]))

            case ExprTy.Index:
                raise NotImplementedError

            case ExprTy.Binary:
                raise NotImplementedError

            case ExprTy.Unary:
                raise NotImplementedError

            case ExprTy.Comparison:
                raise NotImplementedError

            case _:
                raise NotImplementedError
