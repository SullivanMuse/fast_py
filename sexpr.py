import re


def parse(s):
    tokens = tokenize(s)
    expr = parse_expr(tokens)
    if tokens:
        raise ValueError("Unexpected tokens remaining: " + " ".join(iter(lambda: tokens.next(), None)))
    return expr


def tokenize(s):
    return Peek(re.findall(r'\(|\)|[^\s()]+', s))


class Peek:
    def __init__(self, it):
        self.it = iter(it)
        self._peek = next(self.it, None)

    def __bool__(self):
        return self.peek() is not None

    def next(self):
        if self._peek is not None:
            out = self._peek
            self._peek = None
            return out
        return next(self.it, None)

    def peek(self):
        if self._peek is None:
            self._peek = next(self.it, None)
        return self._peek


def parse_expr(tokens):
    token = tokens.peek()
    if token == "(":
        tokens.next()
        exprs = list(iter(lambda: parse_expr(tokens), None))
        if tokens.next() != ")":
            raise ValueError('Unclosed "("')
        return exprs
    elif token == ")":
        return
    elif token is None:
        return
    else:
        tokens.next()
        return parse_atom(token)


def parse_atom(token):
    if token is None:
        raise ValueError
    try:
        return int(token)
    except ValueError:
        try:
            return float(token)
        except ValueError:
            return token


if __name__ == "__main__":
    print(parse("(fn hello (1 2 3) ())"))
