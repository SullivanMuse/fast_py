from dataclasses import dataclass

@dataclass
class Value:
    pass

@dataclass
class Integer(Value):
    value: int

@dataclass
class IntegerType(Value):
    pass

@dataclass
class TypeType(Value):
    pass
