import heapq

def toposort(deps):
    nodes = set(deps)
    for v in deps.values():
        nodes.update(v)
    indeg = {n: 0 for n in nodes}
    rev = {n: [] for n in nodes}
    for n, ds in deps.items():
        for d in set(ds):
            indeg[n] += 1
            rev[d].append(n)
    heap = [n for n in nodes if indeg[n] == 0]
    heapq.heapify(heap)
    out = []
    while heap:
        n = heapq.heappop(heap)
        out.append(n)
        for m in rev[n]:
            indeg[m] -= 1
            if indeg[m] == 0:
                heapq.heappush(heap, m)
    if len(out) != len(nodes):
        raise ValueError("cycle")
    return out
