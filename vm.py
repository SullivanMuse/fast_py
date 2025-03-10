from dataclasses import dataclass, field
from typing import Any, Optional

from errors import VmError
from instr import (
    Arg,
    ArrayExtend,
    ArrayPush,
    Assert,
    Call,
    Cap,
    ClosureNew,
    Imm,
    Instr,
    LocalJump,
    Ref,
    Stack,
    Pop,
    Push,
    Return,
)
from mixins import Format
from value import Bool, Closure, Value
from compile import compile


@dataclass
class StackFrame(Format):
    closure: Closure
    args: list[Any]
    locals: list[Any] = field(default_factory=list)

    def positional(self):
        yield self.closure
        yield self.args
        yield from self.locals


@dataclass
class Vm(Format):
    stack: list[StackFrame] = field(default_factory=lambda: [])

    def positional(self):
        yield from self.stack

    @property
    def frame(self):
        return self.stack[-1]

    def push_frame(self, closure):
        if len(self.stack) == 0:
            assert closure.spec.n_args == 0, "First closure run must not have arguments"
            args = []
        else:
            n_args = closure.spec.n_args
            self.frame.locals, args = (
                self.frame.locals[:-n_args],
                self.frame.locals[-n_args:],
            )
        self.stack.append(StackFrame(closure, args))

    def pop_frame(self) -> StackFrame:
        return self.stack.pop()

    def resolve(self, arg) -> Value:
        if not isinstance(arg, Ref):
            raise TypeError
        match arg:
            case Arg(index):
                return self.frame.args[index]

            case Cap(index):
                return self.frame.closure.captures[index]

            case Imm(value):
                return value

            case Stack(index):
                return self.frame.locals[index]

            case _:
                raise NotImplementedError(f"`Vm.resolve({type(arg).__name__})`")

    def push(self, value):
        self.frame.locals.append(value)

    def ret(self, value_ref):
        return_value = self.resolve(value_ref)
        self.pop_frame()
        return return_value

    def run(self, closure: list[Instr] | Closure) -> Value:
        self.closure = closure

        # Push the new frame
        self.push_frame(closure)
        code = closure.spec.code

        ip = 0
        while ip in range(len(code)):
            instr = code[ip]
            match instr:
                case Push(value_ref):
                    value = self.resolve(value_ref)
                    self.push(value)

                case Call():
                    closure = self.resolve(instr.closure)
                    value = self.run(closure)
                    self.push(value)

                case ClosureNew(spec):
                    captures = [self.frame[i] for i in spec.capture_indices]
                    closure = Closure(spec, captures)
                    self.push(closure)

                case ArrayPush(dest_ref, item_ref):
                    dest = self.resolve(dest_ref)
                    item = self.resolve(item_ref)
                    dest.values.append(item)

                case ArrayExtend(dest_ref, source_ref):
                    dest = self.resolve(dest_ref)
                    source = self.resolve(source_ref)
                    dest.values.extend(source.values)

                case LocalJump(condition_ref, dest):
                    condition = self.resolve(condition_ref)
                    if condition == Bool(True):
                        ip = dest
                        continue

                case Return(return_value_ref):
                    return self.ret(return_value_ref)

                case Pop():
                    self.frame.locals.pop()

                case Assert():
                    value = self.resolve(instr.value)
                    if value != Bool(True):
                        raise VmError(f"assertion error: {instr.reason}")

                case _:
                    raise NotImplementedError(
                        f"`Vm.run` missing case for instruction: {instr}"
                    )

            ip += 1
        return self.ret(Stack(-1))


def run(code):
    if isinstance(code, str):
        code = compile(code)
    vm = Vm()
    return vm.run(code)
