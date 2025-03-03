from dataclasses import dataclass, field

from instr import (
    ArrayExtend,
    ArrayPush,
    Call,
    ClosureNew,
    Imm,
    Instr,
    Jump,
    Local,
    Pop,
    Push,
    Return,
)
from value import Bool, Closure, Value


@dataclass
class Vm:
    stack: list[list[Value]] = field(default_factory=lambda: [[]])

    @property
    def frame(self):
        return self.stack[-1]

    def push_frame(self, take_args):
        self.stack.append(self.frame[-take_args:])

    def pop_frame(self) -> list[Value]:
        return self.stack.pop()

    def resolve(self, arg) -> Value:
        match arg:
            case Imm(value):
                return value

            case Local(ix):
                return self.frame[ix]

            case _:
                raise TypeError

    def push(self, value):
        self.frame.append(value)

    def run(self, closure: list[Instr] | Closure) -> Value:
        if not isinstance(closure, Closure):
            closure = Closure.from_code(closure)

        self.push_frame(closure.spec.n_args)
        self.frame.extend(closure.captures)
        code = closure.spec.code

        instr_ix = 0
        while True:
            if instr_ix not in range(len(code)):
                raise ValueError(
                    f"instruction pointer ({instr_ix}) out of range ({len(code) = }); bad code"
                )

            match instr := code[instr_ix]:
                case Push(value_ref):
                    value = self.resolve(value_ref)
                    self.push(value)

                case Call(closure_ref):
                    closure = self.resolve(closure_ref)
                    self.push(self.run(closure))

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

                case Jump(condition_ref, dest_index):
                    condition = self.resolve(condition_ref)
                    if condition == Bool(True):
                        instr_ix = dest_index
                        continue

                case Return(return_value_ref):
                    return_value = self.resolve(return_value_ref)
                    self.pop_frame()
                    return return_value

                case Pop():
                    self.frame.pop()

                case _:
                    raise NotImplementedError(
                        f"`Vm.run` missing case for instruction: {instr}"
                    )

            instr_ix += 1


def run(closure):
    return Vm().run(closure)
