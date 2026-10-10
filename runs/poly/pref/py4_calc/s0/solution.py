import re

def evaluate(expr):
    toks = re.findall(r"\d+\.?\d*|\.\d+|[-+*/()]|\S", expr)
    for t in toks:
        if not re.fullmatch(r"\d+\.?\d*|\.\d+|[-+*/()]", t):
            raise ValueError("bad token")
    pos = [0]

    def peek():
        return toks[pos[0]] if pos[0] < len(toks) else None

    def take():
        t = peek()
        pos[0] += 1
        return t

    def expr_():
        v = term()
        while peek() in ("+", "-"):
            op = take()
            r = term()
            v = v + r if op == "+" else v - r
        return v

    def term():
        v = factor()
        while peek() in ("*", "/"):
            op = take()
            r = factor()
            if op == "*":
                v *= r
            else:
                if r == 0:
                    raise ZeroDivisionError
                v /= r
        return v

    def factor():
        t = take()
        if t is None:
            raise ValueError("unexpected end")
        if t == "-":
            return -factor()
        if t == "(":
            v = expr_()
            if take() != ")":
                raise ValueError("missing )")
            return v
        if re.fullmatch(r"\d+\.?\d*|\.\d+", t):
            return float(t)
        raise ValueError("unexpected " + t)

    if not toks:
        raise ValueError("empty")
    v = expr_()
    if pos[0] != len(toks):
        raise ValueError("trailing")
    return v
