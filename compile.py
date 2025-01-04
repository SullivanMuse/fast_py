# builtin
from dataclasses import dataclass, field
from typing import Optional

# project
from comb import Span
from vm.instr import Im, InstrTy
from tree import Expr, Node, Statement
from vm.value import Value, ValueTy


@dataclass
class Scope:
    prev: Optional["Scope"] = None
    map: dict[str, int] = field(default_factory=dict)
    anon_count: int = 0

    def __getitem__(self, key) -> int:
        try:
            return self.map[key]
        except KeyError:
            if self.prev is None:
                raise KeyError
            return self.prev[key]

    def __setitem__(self, key, value):
        self.map[key] = value

    def anon(self) -> int:
        ix = len(self.map) + self.anon_count
        self.anon_count += 1
        return ix


@dataclass
class FnSpec:
    captures: list[int]
    code: list[Node]
    result_ix: int


@dataclass
class CompileError(Exception):
    span: Span
    reason: str


@dataclass
class Compiler:
    scope: Scope = field(default_factory=Scope)
    code: list[Node] = field(default_factory=list)

    def push(self, code: Node) -> int:
        self.code.append(code)
        match code.ty:
            case InstrTy.Push:
                ix = self.scope.anon()

            case InstrTy.Call:
                ix = self.scope.anon()

            case InstrTy.Array:
                ix = self.scope.anon()

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
            case Statement.Expr:
                return self.compile_expr(statement.children[0])

            case _:
                raise NotImplementedError

    def compile_scope(self, statements: list[Statement]) -> int:
        self.scope = Scope(self.scope)
        result_ix = None
        for statement in statements:
            result_ix = self.compile_statement(statement)
        if result_ix is None:
            instr = Node(InstrTy.Push, [Im(Value(ValueTy.Unit))])
            result_ix = self.push(instr)
        self.scope = self.scope.prev
        return result_ix

    def compile_expr(self, expr: Node) -> int:
        match expr.ty:
            case Expr.Id:
                id = expr.span.str()
                item_ix = self.scope[id]
                instr = Node(InstrTy.Local, [item_ix])
                return self.push(instr)

            case Expr.Int:
                value = Value(ValueTy.Int, [int(expr.span.str())])
                instr = Node(ty=InstrTy.Push, children=[value])
                return self.push(instr)

            case Expr.Tag:
                value = Value(ValueTy.Tag, [expr.span.str()])
                instr = Node(InstrTy.Push, [value])
                return self.push(instr)

            case Expr.Float:
                value = Value(ValueTy.Float, [float(expr.span.str())])
                instr = Node(InstrTy.Push, [value])
                return self.push(instr)

            case Expr.String:
                raise NotImplementedError

            case Expr.Array:
                length = Im(Value(ValueTy.Int, len(expr.children)))
                instr = Node(InstrTy.Array, [length])
                array_ix = Im(Value(ValueTy.Int, [self.push(instr)]))
                for child in expr.children:
                    if child.ty == Expr.Spread:
                        item_ix = Im(Value(ValueTy.Int, [self.compile_expr(child.child)]))
                        instr = Node(InstrTy.ArrayExtend, [array_ix, item_ix])
                    else:
                        item_ix = Im(Value(ValueTy.Int, [self.compile_expr(child)]))
                        instr = Node(InstrTy.ArrayPush, [array_ix, item_ix])
                    self.push(instr)
                return array_ix

            case Expr.Spread:
                raise CompileError("Spread expression outside of array literal")

            case Expr.Paren:
                return self.compile_expr(expr.children[0])

            case Expr.Fn:
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
                spec = FnSpec(captures.values(), new_compiler.code, result_ix)

                return self.push(Node(InstrTy.Closure, [spec]))

            case Expr.Block:
                return self.compile_scope(expr.children)

            case Expr.Match:
                raise NotImplementedError

            case Expr.Loop:
                raise NotImplementedError

            case Expr.Call:
                fn_ix = self.compile_expr(expr.children[0])
                args_ix = []
                for child in expr.children[1:]:
                    args_ix.append(self.compile_expr(child))
                for arg_ix in args_ix:
                    self.push(Node(InstrTy.Push, [Im(Value(ValueTy.Int, [arg_ix]))]))
                return self.push(Node(InstrTy.Call, [Im(Value(ValueTy.Int, [fn_ix]))]))

            case Expr.Index:
                raise NotImplementedError

            case Expr.Binary:
                raise NotImplementedError

            case Expr.Unary:
                raise NotImplementedError

            case Expr.Comparison:
                raise NotImplementedError

            case _:
                raise NotImplementedError
