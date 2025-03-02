class FormatNode:
    """FormatNode is a mixin class that allows pretty-printing of tree and graph data structures. Simply define `self.short` and `self.children`. Depth-limiting, cycle detection, and"""

    # - Required -#
    def short(self):
        return type(self).__name__

    def children(self):
        yield from ()

    # - Convenience -#
    @property
    def child(self):
        """Get lone child if there is one, or raise ValueError"""
        if len(self.children) != 1:
            raise ValueError
        return self.children[0]

    @property
    def left(self):
        """Get left child if there are exactly 2 children, or raise ValueError"""
        if len(self.children) != 2:
            raise ValueError
        return self.children[0]

    @property
    def right(self):
        """Get right child if there are exactly 2 children, or raise ValueError"""
        if len(self.children) != 2:
            raise ValueError
        return self.children[1]

    def __iter__(self):
        yield from self.children()

    # - Pretty-printing -#
    def pretty_lines(self, recursive=True, max_depth=10, visited=None, depth=0):
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
        indent = "  " * depth
        if id(self) in visited:
            yield f"{indent}{self.short()} <cycle>"
            return
        visited.add(id(self))
        yield f"{indent}{self.short()}"
        if not recursive:
            return
        for child in self.children():
            if depth + 1 >= max_depth:
                yield f"{indent}  <exceeded max depth of {max_depth}>"
                break
            elif isinstance(child, FormatNode):
                yield from child.pretty_lines(recursive, max_depth, visited, depth + 1)
            else:
                yield f"{indent}  {child}"

    def pretty(self, **kwargs):
        """Convenience function for generating str from self.pretty_lines() generator

        Returns:
            str: Pretty str representation of self
        """
        return "\n".join(self.pretty_lines(**kwargs))

    def p(self, recursive=True, max_depth=10, **kwargs):
        """Convenience method for printing data structure

        Args:
            recursive (bool, optional): Recurse or just print shallow repr? Defaults to True.
            max_depth (int, optional): Maximum depth to print. Defaults to 10.
        """
        print(self.pretty(recursive=recursive, max_depth=max_depth), **kwargs)

    def __str__(self):
        return self.pretty()


class GetChildren:
    """Use this method to add the subclasses of a class to its namespace"""

    @classmethod
    def get_children(cls):
        for sub in cls.__subclasses__():
            setattr(cls, sub.__name__, sub)
