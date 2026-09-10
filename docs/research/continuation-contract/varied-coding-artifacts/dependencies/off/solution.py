import heapq


def schedule(graph):
    if not isinstance(graph, dict):
        raise ValueError("graph must be a dict")

    nodes = set()
    dependencies = {}

    for node, deps in graph.items():
        if not isinstance(node, str) or not node:
            raise ValueError("node IDs must be nonempty strings")
        if not isinstance(deps, (list, tuple)):
            raise ValueError("dependencies must be lists or tuples")

        nodes.add(node)
        unique_deps = set()
        for dependency in deps:
            if not isinstance(dependency, str) or not dependency:
                raise ValueError("dependency IDs must be nonempty strings")
            unique_deps.add(dependency)
            nodes.add(dependency)
        dependencies[node] = unique_deps

    dependents = {node: set() for node in nodes}
    remaining = {node: 0 for node in nodes}
    for node, deps in dependencies.items():
        remaining[node] = len(deps)
        for dependency in deps:
            dependents[dependency].add(node)

    ready = [node for node, count in remaining.items() if count == 0]
    heapq.heapify(ready)
    order = []
    while ready:
        node = heapq.heappop(ready)
        order.append(node)
        for dependent in dependents[node]:
            remaining[dependent] -= 1
            if remaining[dependent] == 0:
                heapq.heappush(ready, dependent)

    if len(order) != len(nodes):
        raise ValueError("graph contains a cycle")
    return order
