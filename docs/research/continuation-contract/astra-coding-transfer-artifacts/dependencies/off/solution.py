import heapq


def schedule(graph):
    """Return the lexicographically smallest dependency-first ordering."""
    if not isinstance(graph, dict):
        raise ValueError("graph must be a dict")

    dependencies = {}
    for node, required in graph.items():
        if not isinstance(node, str) or not node:
            raise ValueError("node IDs must be nonempty strings")
        if not isinstance(required, (list, tuple)):
            raise ValueError("dependencies must be a list or tuple")
        unique = set()
        for dependency in required:
            if not isinstance(dependency, str) or not dependency:
                raise ValueError("dependency IDs must be nonempty strings")
            unique.add(dependency)
        dependencies[node] = unique

    dependents = {node: [] for node in dependencies}
    indegree = {node: len(required) for node, required in dependencies.items()}
    for node, required in dependencies.items():
        for dependency in required:
            indegree.setdefault(dependency, 0)
            dependents.setdefault(dependency, []).append(node)

    ready = [node for node, degree in indegree.items() if degree == 0]
    heapq.heapify(ready)
    order = []
    while ready:
        node = heapq.heappop(ready)
        order.append(node)
        for dependent in dependents[node]:
            indegree[dependent] -= 1
            if indegree[dependent] == 0:
                heapq.heappush(ready, dependent)

    if len(order) != len(indegree):
        raise ValueError("graph contains a cycle")
    return order
