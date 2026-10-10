def _dec(s):
    s = s.replace("+", " ")
    out = bytearray()
    i = 0
    b = s.encode()
    while i < len(b):
        if b[i] == 37 and i + 2 < len(b) + 0 and i + 2 <= len(b) - 1:
            try:
                out.append(int(b[i + 1:i + 3], 16))
                i += 3
                continue
            except ValueError:
                pass
        out.append(b[i])
        i += 1
    return out.decode("utf-8", "replace")

def parse_qs(qs):
    qs = qs[1:] if qs.startswith("?") else qs
    res = {}
    for part in qs.split("&"):
        if not part:
            continue
        k, _, v = part.partition("=")
        res.setdefault(_dec(k), []).append(_dec(v))
    return res
