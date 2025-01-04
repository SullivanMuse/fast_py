class FormatNode:
    def str(self):
        raise NotImplementedError

    @property
    def child(self):
        if len(self.children) != 1:
            raise ValueError
        return self.children[0]

    @property
    def left(self):
        if len(self.children) != 2:
            raise ValueError
        return self.children[0]

    @property
    def right(self):
        if len(self.children) != 2:
            raise ValueError
        return self.children[1]

    def __iter__(self):
        return iter(self.children)

    def _str_impl(self, depth=0):
        children_str = "\n".join(
            child._str_impl(depth + 1)
            for child in self
            if isinstance(child, FormatNode)
        )
        children_str1 = "" if len(self.children) == 0 else f"\n{children_str}"
        return f"{'  ' * depth}{self.str()}{children_str1}"

    def __str__(self):
        return self._str_impl()
