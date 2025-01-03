def comma_and(it, oxford=True, zero_output="", nonzero_prefix=""):
    """
    [] => ""
    [1] => 1
    [1, 2] => 1 and 2
    [1, 2, 3] => 1, 2[,] and 3
    [1, 2, 3, 4] => 1, 2, 3[,] and 4
    """
    it = iter(it)
    try:
        first = next(it)
    except StopIteration:
        return zero_output
    try:
        second = next(it)
    except StopIteration:
        return f"{nonzero_prefix}{first}"
    try:
        prev = next(it)
    except StopIteration:
        return f"{nonzero_prefix}{first} and {second}"
    out = f"{nonzero_prefix}{first}, {second}"
    for item in it:
        out += f", {prev}"
        prev = item
    out += f", and {prev}" if oxford else f" and {prev}"
    return out


def count_str(noun, count):
    if count == 0:
        return ""
    elif count == 1:
        return f"1 {noun}"
    else:
        return f"{count} {noun}s"

if __name__ == "__main__":
    addons = {
        "milk": 1,
        "sugar": 2,
        "cream": 3,
    }
    print(comma_and(map(lambda kv: count_str(*kv), addons.items()), nonzero_prefix="with "))
