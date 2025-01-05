from dataclasses import dataclass, field

from vm.value import Value
from vm.instr import Im, InstrTy, Loc


@dataclass
class Vm:
    stack: list[list[Value]] = field(default_factory=list)

    def resolve(self, arg):
        match arg:
            case Im(ix):
                return ix

            case Loc(ix):
                return self.stack[-1][ix]

            case _:
                raise ValueError

    def run(self, code: list, locals):
        self.stack.append(locals)
        for code in code:
            match code.ty:
                case InstrTy.Push:
                    self.stack[-1].append(code.child)

                case InstrTy.Call:
                    closure = self.resolve(code.child)
                    spec = closure.child
                    args = [self.resolve(Loc(-1-n)) for n in reversed(range(spec.args))]
                    captures = 
                    self.run(spec.code, [args, captures])

                case _:
                    raise NotImplementedError
