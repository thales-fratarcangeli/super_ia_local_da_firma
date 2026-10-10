from collections import deque

def shortest_path(grid, start, goal):
    R, C = len(grid), len(grid[0]) if grid else 0
    for r, c in (start, goal):
        if not (0 <= r < R and 0 <= c < C) or grid[r][c] == "#":
            raise ValueError("invalid")
    q = deque([(start, 0)])
    seen = {start}
    while q:
        (r, c), d = q.popleft()
        if (r, c) == goal:
            return d
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            n = (r + dr, c + dc)
            if 0 <= n[0] < R and 0 <= n[1] < C and grid[n[0]][n[1]] != "#" and n not in seen:
                seen.add(n)
                q.append((n, d + 1))
    return -1
