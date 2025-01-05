from dataclasses import dataclass, field

from vm.value import Closure, Value, ValueTy
from vm.instr import Imm, InstrTy, Loc


@dataclass
class Vm:
    stack: list[list[Value]] = field(default_factory=list)

    @property
    def frame(self):
        return self.stack[-1]

    def push_frame(self, take_args):
        self.stack.append(self.stack[-1][-take_args:])

    def pop_frame(self) -> list[Value]:
        return self.stack.pop()

    def resolve(self, arg) -> Value:
        match arg:
            case Imm(value):
                return value

            case Loc(ix):
                return self.stack[-1][ix]

            case _:
                raise TypeError

    def run(self, code: list):
        for instr in code:
            match instr.ty:
                case InstrTy.Push:
                    self.stack[-1].append(self.resolve(instr.child))

                case InstrTy.Call:
                    closure = self.resolve(instr.child).child

                    # Push frame and take args
                    self.push_frame(closure.spec.args)
                    self.stack[-1].extend(closure.captures)

                    # Run the code
                    self.run(closure.spec.code)

                    frame = self.pop_frame()
                    self.frame.append(frame[-1])

                case InstrTy.Closure:
                    spec = instr.child
                    captures = [self.frame[i] for i in spec.captures]
                    self.frame.append(Value(ValueTy.Closure, [Closure(spec, captures)]))

                case _:
                    raise NotImplementedError
