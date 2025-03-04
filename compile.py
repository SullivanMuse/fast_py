from dataclasses import dataclass, field
from typing import Optional

from errors import CompileError
from instr import (
    Arg,
    ArrayExtend,
    ArrayPush,
    Assert,
    Call,
    Cap,
    ClosureNew,
    LocalJump,
    Stack,
    MatchArray,
    Pop,
    Push,
    Ref,
    StringBufferPush,
    StringBufferToString,
)
from parse import statements
from tree import (
    ArrayExpr,
    ArrayPattern,
    BinaryExpr,
    BlockExpr,
    CallExpr,
    ComparisonExpr,
    Expr,
    ExprStatement,
    FloatExpr,
    FnExpr,
    FnStatement,
    GatherPattern,
    IdExpr,
    IdPattern,
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
class Frame:
    _captures: dict[str, int] = field(default_factory=dict)
    _args: dict[str, int] = field(default_factory=dict)

    # For keeping track of locals and temporaries
    _locals: list[dict[str, Ref]] = field(default_factory=lambda: [{}])
    _curr_frame_size: list[int] = field(default_factory=lambda: [0])
    _max_frame_size: int = 0

    def push_scope(self):
        self._locals.append({})
        self._curr_frame_size.append(self._curr_frame_size[-1])

    def pop_scope(self) -> int:
        popped = self._locals.pop()
        return popped

    def __getitem__(self, key) -> Ref:
        for scope in reversed(self._locals):
            if key in scope:
                return scope[key]
        if key in self._args:
            return Arg(self._args[key])
        elif key in self._captures:
            return Cap(self._captures[key])
        raise KeyError(f"Undefined reference to {key}")

    def loc(self, key, ref):
        self._locals[-1][key] = ref

    def arg(self, key):
        index = len(self._args)
        self._args[key] = index

    def cap(self, key):
        index = len(self._captures)
        self._captures[key] = index

    def push(self) -> Stack:
        """Increase stack depth"""
        self._curr_frame_size[-1] += 1
        self._max_frame_size = max(self._curr_frame_size[-1], self._max_frame_size)
        return self.top()

    def pop(self):
        """Reduce stack depth"""
        self._curr_frame_size[-1] -= 1

    def top(self) -> Stack:
        if self._curr_frame_size[-1] != 0:
            return Stack(self._curr_frame_size[-1] - 1)


@dataclass
class Compiler:
    frame: Frame = field(default_factory=Frame)
    code: list[SyntaxNode] = field(default_factory=list)

    def push_code(self, instr: Instr) -> Optional[Ref]:
        """Push the instruction into the code object

        Args:
            instr (Instr): The instruction to push

        Raises:
            NotImplementedError: The instruction type is not implemented

        Returns:
            Optional[Loc]: The location of the value pushed on the stack by the instruction, if any
        """
        self.code.append(instr)

        ref = None
        match instr:
            case Push():
                ref = self.frame.push()

            case ArrayPush(ref):
                self.frame.pop()

            case ArrayExtend(array_loc, item_ref):
                pass

            case ClosureNew(spec):
                ref = self.frame.push()

            case Call():
                for _ in range(instr.n_args):
                    self.frame.pop()
                ref = self.frame.push()

            case LocalJump():
                self.frame.pop()

            case Pop():
                self.frame.pop()

            case StringBufferPush():
                pass

            case StringBufferToString():
                ref = self.frame.push()

            case Assert():
                pass

            case _:
                raise NotImplementedError(f"`Compiler.push({type(instr).__name__})`")

        return ref

    def compile_pattern(self, pattern: Pattern, irrefutable=False) -> Stack:
        """Attempts to match the value on the top of the stack

        Args:
            pattern (Pattern): The pattern to match

        Raises:
            NotImplementedError: The given pattern type is not implemented

        Returns:
            Optional[int]: The stack location of the boolean value indicating whether the pattern matched or not, unless the pattern does not branch
        """
        print(f"`Compiler.compile_pattern({type(pattern)})`")
        match pattern:
            case IdPattern():
                # Top of the stack is the last result compiled
                ref = self.frame.top()
                if pattern.inner is not None:
                    self.compile_pattern(pattern.inner)
                self.frame.loc(pattern.name.str(), ref)
                return self.push_code(Push(Bool(True)))

            case ArrayPattern():
                lower_bound = sum(
                    1 for x in pattern.items if not isinstance(x, GatherPattern)
                )
                return self.push_code(MatchArray(lower_bound))

            case _:
                raise NotImplementedError(
                    f"`Compiler.compile_pattern({type(pattern).__name__})`"
                )

    def compile_statement(self, statement: Statement) -> Optional[Stack]:
        """Compile the statement

        Args:
            statement (Statement): The statement to compile

        Raises:
            NotImplementedError: The statement type is not implemented

        Returns:
            Optional[Loc]: The location of the value produced by the statement
        """
        print(f"`Compiler.compile_statement({type(statement)})`")
        match statement:
            case ExprStatement():
                return self.compile_expr(statement.inner)

            case LetStatement():
                self.compile_expr(statement.inner)
                ix = self.compile_pattern(statement.pattern)
                instr = Assert(ix, f"Irrefutable pattern: {statement.pattern}")
                return self.push_code(instr)

            case FnStatement():
                pass

            case _:
                raise NotImplementedError(
                    f"`Compiler.compile_statement({type(statement)})`"
                )

    def compile_statements(self, statements: list[Statement]) -> Optional[Stack]:
        """Compile a series of statements

        Args:
            statements (list[Statement]): The statements to compile

        Returns:
            Optional[Loc]: The location of the value created by the final statement, if any
        """
        self.frame.push_scope()
        result = None
        for statement in statements:
            result = self.compile_statement(statement)
        if result is None:
            instr = Push(Ref.Imm(Unit()))
            result = self.push_code(instr)
        self.frame.pop_scope()
        return result

    def compile_expr(self, expr: Expr) -> Stack:
        """Compile the expression

        Args:
            expr (Expr): The expression to compile

        Raises:
            CompileError: Spread expression appears outside of an array literal
            NotImplementedError: The expression type is not implemented

        Returns:
            Loc: The location of the value produced by the expression
        """
        print(f"`Compiler.compile_expr({type(expr)})`")
        match expr:
            case IdExpr():
                name = expr.span.str()
                ref = self.frame[name]
                instr = Push(ref)
                return self.push_code(instr)

            case IntExpr():
                value = Int(int(expr.span.str()))
                instr = Push(Ref.Imm(value))
                return self.push_code(instr)

            case TagExpr():
                value = Tag(expr.span.str())
                instr = Push(Ref.Imm(value))
                return self.push_code(instr)

            case FloatExpr():
                value = Float(float(expr.span.str()))
                instr = Push(Ref.Imm(value))
                return self.push_code(instr)

            case StringExpr():
                # in the special case that there is only one char and no interpolants, simply create the value in-place
                value = String(expr.chars[0].str())
                instr = Push(Ref.Imm(value))
                ix = self.push_code(instr)

                # For the rest of the interpolants and the chars following them:
                if len(expr.interpolants):
                    instr = Push(Ref.Imm(StringBuffer([ix])))
                    buf_ix = self.push_code(instr)

                    for interpolant, char in zip(expr.interpolants, expr.chars[1:]):
                        # Compile interpolant
                        interp_ix = self.compile_expr(interpolant)
                        instr = StringBufferPush(buf_ix, interp_ix)
                        self.push_code(instr)

                        # Compile char
                        instr = Push(Ref.Imm(String(char.str())))
                        piece_ix = self.push_code(instr)
                        instr = StringBufferPush(buf_ix, piece_ix)
                        self.push_code(instr)

                    instr = StringBufferToString(buf_ix)
                    ix = self.push_code(instr)

                # apply fn
                if expr.fn is not None:
                    self.compile_expr(expr.fn)
                    instr = Call(self.frame[expr.fn.span.str()], 1)
                    ix = self.push_code(instr)

                return ix

            case ArrayExpr():
                instr = Push(Array([None] * len(expr.items)))
                array_loc = self.push_code(instr)
                for item in expr.items:
                    match item:
                        case Spread():
                            ref = self.compile_expr(item.inner)
                            instr = ArrayExtend(array_loc, ref)

                        case _:
                            ref = self.compile_expr(item)
                            instr = ArrayPush(array_loc, ref)
                    self.push_code(instr)
                return array_loc

            case Spread():
                raise CompileError("Spread expression outside of array literal")

            case ParenExpr():
                return self.compile_expr(expr.inner)

            case FnExpr():
                # Compute free variables
                free = set(expr.free())

                # Collect indices of captured variables
                captures = {}
                for k in free:
                    captures[k] = self.frame[k]

                # Create new scope for function and allocate space for captured variables
                scope = Frame()
                for k in free:
                    scope.cap(k)

                # Allocate space for function arguments
                for pat in expr.params:
                    for var in pat.bound():
                        scope.arg(var)

                # Compile the function
                new_compiler = Compiler(scope)
                result_ix = new_compiler.compile_expr(expr.inner)
                spec = ClosureSpec(
                    new_compiler.code, len(expr.params), list(captures.values())
                )

                return self.push_code(ClosureNew(spec))

            case BlockExpr():
                return self.compile_statements(expr.statements)

            case MatchExpr():
                raise NotImplementedError

            case LoopExpr():
                raise NotImplementedError

            case CallExpr():
                # Calling convention:
                #   x y z -> return value
                fn_ix = self.compile_expr(expr.fn)
                for arg in expr.args:
                    self.compile_expr(arg)
                return self.push_code(Call(fn_ix, len(expr.args)))

            case IndexExpr():
                raise NotImplementedError

            case BinaryExpr():
                raise NotImplementedError

            case UnaryExpr():
                raise NotImplementedError

            case ComparisonExpr():
                raise NotImplementedError

            case _:
                raise NotImplementedError(f"`Compiler.compile_expr({type(expr)})`")

    def into_closure(self) -> Closure:
        """Turn the code object from the compiler into a Closure and clear the compiler

        Returns:
            Closure: The closure produced from the code object
        """
        closure = Closure(ClosureSpec(self.code, 0, []), [])
        self.frame = Frame()
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
