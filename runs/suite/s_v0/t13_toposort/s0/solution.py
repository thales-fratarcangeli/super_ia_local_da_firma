from collections import defaultdict, deque

def toposort(deps: dict[str, list[str]]) -> list[str]:
    graph = defaultdict(list)
    in_degree = defaultdict(int)
    all_nodes = set()

    for node, dependencies in deps.items():
        all_nodes.add(node)
        for dep in dependencies:
            graph[dep].append(node)
            in_degree[node] += 1
            all_nodes.add(dep)

    queue = deque()
    for node in all_nodes:
        if in_degree[node] == 0:
            queue.append(node)

    result = []
    while queue:
        node = min(queue)
        result.append(node)
        for neighbor in graph[node]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    if len(result) != len(all_nodes):
        raise ValueError("Ciclo detectado")

    return result
