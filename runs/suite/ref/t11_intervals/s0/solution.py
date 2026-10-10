def merge_intervals(intervals):
    for a, b in intervals:
        if a > b:
            raise ValueError("invalid")
    out = []
    for a, b in sorted(intervals):
        if out and a <= out[-1][1]:
            out[-1] = (out[-1][0], max(out[-1][1], b))
        else:
            out.append((a, b))
    return out
