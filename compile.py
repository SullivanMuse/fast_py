import collections
import dataclasses

import instr
import parse
import tree
import value


@dataclasses.dataclass
class Compiler:
    """
    function compiler

    has member variables for tracking local variables, captured (free) variables, labels, and for accumulating instructions
    """
    depths: list[int] = dataclasses.field(default_factory=lambda: [0])
    scopes: collections.ChainMap[str, int] = dataclasses.field(default_factory=collections.ChainMap)
    captures: dict[str, int] = dataclasses.field(default_factory=list)
    labels: collections.Counter = dataclasses.field(default_factory=collections.Counter)
    code: list[instr.Instr] = dataclasses.field(default_factory=list)

    # scope handling
    # ==============
    def enter(self):
        """enter scope"""
        self.scopes = self.scopes.new_child()
        self.depths.append(self.depths[-1])

    def exit(self):
        """exit scope"""
        assert len(self.scopes.maps) > 1 and len(self.depths) == len(self.scopes.map), "exit must match an enter"
        self.scopes = self.scopes.parents()
        self.depths.pop()

    # variables handling
    # ===============
    def local_count(self):
        """number of distinct local declarations seen"""
        return sum(map(len, self.scopes.maps))

    def get(self, key):
        """local or capture"""
        if (out := self.scopes.get(key)) is not None:
            return instr.GetLocal(out)
        if key not in self.captures:
            self.captures[key] = len(self.captures)
        return instr.GetCap(self.captures[key])

    def captures_list(self):
        """convert order-map to key list"""
        captures = [None] * len(self.captures)
        for k, i in self.captures.items():
            captures[i] = k
        return captures

    def declare(self, key):
        """create a new local variable"""
        self.scopes[key] = self.local_count()

    def create_label(self, prefix=""):
        """create a unique label with optional prefix"""
        n = self.labels[prefix]
        self.labels[prefix] += 1
        return f"{prefix}{n}"

    # instruction handling
    # ====================
    def add(self, instr):
        self.depth[-1] += instr.effect()
        self.code.append(instr)

    # main compilation functions
    # ==========================
    def pattern(self, pattern: tree.Pattern, success: str, failure: str):
        initial_depth = self.depths
        match pattern:
            case _:
                raise NotImplementedError(f"`Compiler.pattern({type(pattern)})`")
        self.jump(success)

        assert self.depths[-1] == initial_depth, "pattern matching should not change stack depth"

    def annotated_pattern(self, pattern: tree.Pattern, success: str, failure: str):
        self.annotate(f"Compiling {pattern}")
        self.pattern(pattern, success, failure)
        self.annotate(f"Done compiling {pattern}")

    def expr(self, expr: tree.Expr):
        match expr:
            case tree.IntExpr():
                self.add(instr.Push(value.Int(int(expr.span.str()))))

            case tree.TagExpr():
                self.add(instr.Push(value.Tag(expr.span.str())))

            case tree.FloatExpr():
                self.add(instr.Push(value.Float(float(expr.span.str()))))

            case tree.FnExpr():
                compiler = Compiler()
                compiler.init(expr)
                captures = [None] * len(compiler.captures)
                for key, index in compiler.captures:
                    captures[index] = self.get(key)
                self.add(instr.MakeClosure(compiler.code, len(expr.params), len(compiler.captures)))

            case tree.MatchExpr():
                self.expr(expr.subject)
                for arm in expr.arms:
                    self.enter()
                    success = self.create_label()
                    failure = self.create_label()
                    self.pattern(arm.pattern, success, failure)
                    self.label(success)
                    self.expr(arm.expr)
                    self.exit()
                    self.failure()

            case _:
                raise NotImplementedError(f"`Compiler.compile_expr({type(expr)})`")

    def init(self, fn: tree.FnExpr):
        for n, pattern in enumerate(fn.params):
            self.declare(f"${n}")

        # pattern matching
        failure = self.create_label()
        for n, pattern in enumerate(fn.params):
            next_param = self.create_label()
            self.get(f"${n}")
            self.annotated_pattern(pattern, next_param, failure)
            self.label(next_param)

        self.expr(fn.inner)
        self.label(failure)
        self.abort(f"Pattern matching failed when attempting to match function args: {fn.span}")


def compile(input: tree.Expr | list[tree.Statement] | str):
    compiler = Compiler()
    if isinstance(input, str):
        res = parse.statements(input)
        compiler.compile_statements(res.val)
    elif isinstance(input, tree.Expr):
        compiler.compile_expr(input)
    elif isinstance(input, list):
        compiler.compile_statements(input)
    else:
        raise TypeError

    return compiler.into_closure()
