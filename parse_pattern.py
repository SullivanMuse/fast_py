from comb import *
from parse_expr import dec_run, name
from tree import *

pattern = Parser()

ignore_pattern = map(seq("_", name), lambda span, _: IgnorePattern(span))
id_pattern = map(name, lambda span, _: IdPattern(span, span))
tag_pattern = map(seq(ignore(":"), name), lambda span, _: TagPattern(span))
integer_pattern = map(dec_run, lambda span, _: IntPattern(span))
float_pattern = not_implemented("float_pattern")
string_pattern = not_implemented("string_pattern")
gather_pattern = starmap(
    seq("..", opt(pattern)),
    GatherPattern,
)


@Parser
def array_pattern_items(s0):
    sep = map(seq(ignore(ws), ",", ignore(ws)), lambda _, sep: sep)
    s = s0

    items = []
    commas = []

    item = alt(pattern, gather_pattern)
    while r := item(s):
        s = r.span
        items.append(r.val)
        if not (r := sep(s)):
            break
        s = r.span
        commas.append(r.val)

    gather_count = sum(1 for item in items if isinstance(item, GatherPattern))
    if gather_count not in (0, 1):
        return Fail(s0.span(s), "Too many gather patterns")

    gather_index = 0
    for item in items:
        if isinstance(item, GatherPattern):
            break
        gather_index += 1
    else:
        gather_index = None

    return Success(s, (items, commas))


array_pattern = starmap(
    seq("[", ignore(ws), array_pattern_items, ignore(ws), "]"),
    lambda span, lsq, items, rsq: ArrayPattern(
        span,
        items[0],
        lsq,
        items[1],
        rsq,
    ),
)

pattern.f = alt(
    ignore_pattern,
    id_pattern,
    tag_pattern,
    integer_pattern,
    float_pattern,
    string_pattern,
    array_pattern,
    gather_pattern,
)
