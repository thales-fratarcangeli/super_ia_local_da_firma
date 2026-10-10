_P = [(1000, "M"), (900, "CM"), (500, "D"), (400, "CD"), (100, "C"), (90, "XC"), (50, "L"), (40, "XL"), (10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I")]

def to_roman(n):
    if not 1 <= n <= 3999:
        raise ValueError("range")
    out = ""
    for v, s in _P:
        while n >= v:
            out += s
            n -= v
    return out

def from_roman(s):
    if not s or not all(c in "IVXLCDM" for c in s):
        raise ValueError("invalid")
    i, total = 0, 0
    for v, sym in _P:
        while s.startswith(sym, i):
            total += v
            i += len(sym)
    if i != len(s) or to_roman(total) != s:
        raise ValueError("invalid")
    return total
