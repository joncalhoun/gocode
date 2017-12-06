import json
from .. import cmd

def autocomplete(position, source):
    out = cmd.must(
        ["gocode", "-f=json", "autocomplete", str(position)],
        source
    )
    ret = json.loads(out)
    return ret


def parse_func(src):
    """
    parse_func is used to parse a Go function into pieces that are easier to use for autocompletion.
    
    Some examples help illustrate it best, so a few are shown below.
    
    Given:
        "func(a int) error"
    parse_func returns:
        ([("a", "int")], "error")
    
    Given:
        "func(a, b int, c chan int, d func(e error) error) (int, error)"
    parse_func returns:
        (
            [
                ("a", "int"),
                ("b", "int"),
                ("c", "chan int"),
                ("d", "func(e error) error"),
            ], 
            "(int, error)"
        )
    
    Return values are not currently parsed because optional named return values make this really hard to do given that return types can have spaces in them and its really hard to differentiate between "name type" and "chan int" or some other similar situation.
    """
    if not src.startswith("func("):
        raise Error("invalid function source: %s" % src)
    
    start = len("func")
    depth = 0
    for i in range(start, len(src)):
        print("i=", i, " src[i]=", src[i])
        if src[i] == "(":
            depth += 1
        elif src[i] == ")":
            depth -= 1
        print("depth=", depth)
        if depth == 0:
            return (parse_params(src[start:i+1]), src[i+1:].strip())
    raise Error("invalid function source: %s" % src)

def parse_params(src):
    """
    Assuming we have input like one of the following:
        (a int)
        (a, b int, c string, f func(int, int) error)
    Parse it and return an array of tuples in the format:
        [(name, type), (name, type)]
    """
    if not (src.startswith("(") and src.endswith(")")):
        raise Error("invalid params: %s" % src)
    
    ret = []
    depth = 0
    lastI = 1
    names = []
    for i in range(0, len(src)):
        char = src[i]
        if char in (",", ")") and depth == 1:
            # End of a param - parse it
            name, _, tipe = src[lastI:i].strip().partition(" ")
            names.append(name)
            lastI = i + 1
            if tipe:
                # Go supports (a, b string) so if we get a
                # type we may need to backfill types
                for n in names:
                    ret.append((n, tipe))
                    names = []
        if char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
    return ret

# def parse_returns(src):
#     """
#     Assuming we have input like one of the following:
#         error
#         func() error
#         (int, error)
#         (i int, e error)
#         (a, b int, e error)
#         (i int, e error, f func(int, string) error)
#     Parse it into individual pieces and return them. This is NOT the same as
#     the parse params and will not return tuples of (name, type) because this is
#     insanely annoying to do when returns can be:
#         - Types with a space in them (eg `chan int` or `func(a, b string) error`)
#         - Named and unnamed (eg `error` or `(i int, e error)`)
#         - And the list goes on...
#     This could probably eventually be supported, but it isn't useful for now.
#     """
#     if not src.startswith("("):
#         # both named returns and multiple returns req parens
#         return [src]
    
#     depth = 0
#     lastI = 1
#     ret = []
#     for i in range(0, len(src)):
#         char = src[i]
#         if char in (",", ")") and depth == 1:
#             ret.append(src[lastI:i].strip())
#             lastI = i + 1
#         if char == "(":
#             depth += 1
#         elif char == ")":
#             depth -= 1
#     return ret

class Error(Exception):
    """gocode errors are always of this type"""
    pass
