from dataclasses import dataclass, fields, is_dataclass, asdict
from typing import Any


class Format:
    """FormatNode is a mixin class that allows pretty-printing of tree and graph data structures. Simply define `self.short` and `self.children`. Depth-limiting, cycle detection, and"""

    # - Required -#
    def short(self):
        """Short representation used when children are hidden"""

        return type(self).__name__

    def named(self):
        """Named children"""

        raise NotImplementedError

    def empty_generator(self):
        yield from ()

    def get_named(self):
        try:
            return self.named()
        except NotImplementedError:
            for pred, proxy in PROXIES:
                if pred(self):
                    try:
                        return proxy(self).named()
                    except NotImplementedError:
                        continue
        raise NotImplementedError

    def positional(self):
        """Positional children"""

        raise NotImplementedError

    def get_positional(self):
        try:
            return self.positional()
        except NotImplementedError:
            for pred, proxy in PROXIES:
                if pred(self):
                    try:
                        return proxy(self).positional()
                    except NotImplementedError:
                        continue
        raise NotImplementedError

    # - Convenience -#
    @property
    def child(self):
        """Get lone child if there is one, or raise ValueError"""
        if len(self.positional) != 1:
            raise ValueError
        return self.positional[0]

    @property
    def left(self):
        """Get left child if there are exactly 2 children, or raise ValueError"""
        if len(self.positional) != 2:
            raise ValueError
        return self.positional[0]

    @property
    def right(self):
        """Get right child if there are exactly 2 children, or raise ValueError"""
        if len(self.positional) != 2:
            raise ValueError
        return self.positional[1]

    # - Pretty-printing -#
    def format_lines(self, recursive=True, max_depth=10, visited=None, depth=0):
        """Pretty-print data structure

        Args:
            recursive (bool, optional): Recurse or just print shallow repr? Defaults to True.
            max_depth (int, optional): Max depth to print. Defaults to 10.
            visited (_type_, optional): Id set for cycle detection; should not be used directly. Defaults to None.
            depth (int, optional): Depth for max depth enforcement; should not be used directly. Defaults to 0.

        Yields:
            str: Lines to print
        """
        if visited is None:
            visited = set()
        indent = "    " * depth
        if id(self) in visited:
            yield f"{indent}{self.short()} <cycle>"
            return
        visited.add(id(self))
        yield f"{indent}{self.short()}"
        if not recursive:
            return

        for key, value in self.get_named():
            yield f"{indent}  {key} = "
            if depth + 1 >= max_depth:
                yield f"{indent}    <exceeded max depth of {max_depth}>"
                return
            p = proxy(value)
            print(f"Selected {type(p)} for proxy for {key}")
            yield from p.format_lines(recursive, max_depth, visited, depth + 1)

        for index, child in enumerate(self.get_positional()):
            if depth + 1 >= max_depth:
                yield f"{indent}    <exceeded max depth of {max_depth}>"
                return

            yield f"{indent}  [{index}] = "
            yield from proxy(child).format_lines(recursive, max_depth, visited, depth + 1)

    def format(self, **kwargs):
        """Convenience function for generating str from self.pretty_lines() generator

        Returns:
            str: Pretty str representation of self
        """
        return "\n".join(self.format_lines(**kwargs))

    def p(self, recursive=True, max_depth=10, **kwargs):
        """Convenience method for printing data structure

        Args:
            recursive (bool, optional): Recurse or just print shallow repr? Defaults to True.
            max_depth (int, optional): Maximum depth to print. Defaults to 10.
        """
        print(self.format(recursive=recursive, max_depth=max_depth), **kwargs)


class FormatList(Format):
    def __init__(self, value):
        self.value = value

    def short(self):
        if self:
            return "[list]"
        else:
            return "[empty list]"

    def positional(self):
        yield from self.value


class FormatTuple(Format):
    def __init__(self, value):
        self.value = value

    def short(self):
        if self:
            return "(tuple)"
        else:
            return "(empty tuple)"

    def positional(self):
        yield from self.value


class FormatDict(Format):
    def __init__(self, value):
        self.value = value

    def short(self):
        if self:
            return "{dict}"
        else:
            return "{empty dict}"

    def named(self):
        yield from sorted(self.value.items())


class FormatDataClass(Format):
    def __init__(self, value):
        self.value = value

    def named(self):
        for field in fields(self.value):
            yield field.name, getattr(self.value, field.name)


class FormatAnything(Format):
    def __init__(self, value):
        self.value = value

    def short(self):
        return str(self.value)

    def positional(self):
        yield from ()

    def named(self):
        yield from ()


PROXIES = [
    (is_dataclass, FormatDataClass),
    (lambda v: isinstance(v, list), FormatList),
    (lambda v: isinstance(v, dict), FormatDict),
    (lambda v: isinstance(v, tuple), FormatTuple),
    (lambda _: True, FormatAnything),
]


def proxy(value):
    if isinstance(value, Format):
        return value
    for pred, proxy in PROXIES:
        if pred(value):
            return proxy(value)
    raise ValueError


def p(value, **kwargs):
    proxy(value).p(**kwargs)


class GetChildren:
    """Use this method to add the subclasses of a class to its namespace"""

    @classmethod
    def get_children(cls):
        for sub in cls.__subclasses__():
            setattr(cls, sub.__name__, sub)
