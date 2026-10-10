def parse_csv_line(line):
    out, cur, i, n = [], [], 0, len(line)
    in_q = False
    while i < n:
        c = line[i]
        if in_q:
            if c == '"':
                if i + 1 < n and line[i + 1] == '"':
                    cur.append('"')
                    i += 1
                else:
                    in_q = False
            else:
                cur.append(c)
        elif c == '"' and not cur:
            in_q = True
        elif c == ",":
            out.append("".join(cur))
            cur = []
        else:
            cur.append(c)
        i += 1
    if in_q:
        raise ValueError("unclosed quote")
    out.append("".join(cur))
    return out
