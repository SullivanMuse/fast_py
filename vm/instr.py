# builtin
from dataclasses import dataclass, field
from enum import auto, Enum
from typing import Any

# project
from vm.value import Value


@dataclass
class Im:
    value: Value


@dataclass
class Loc:
    index: int


class InstrTy(Enum):
    Push = auto() # Push a literal value
    Call = auto() # Call a closure

    # Array
    Array = auto() # Create an array 1 ->
    ArrayPush = auto() # Push an element into an array
