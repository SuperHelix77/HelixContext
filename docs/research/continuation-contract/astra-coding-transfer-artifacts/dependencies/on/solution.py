import heapq


def schedule(graph):
    if not isinstance(graph, dict):
        raise ValueError("graph must be a dict")

    dependencies = {}
    nodes = set()

    for node, deps in graph.items():
        if not isinstance(node, str) or not node:
            raise ValueError("node IDs must be nonempty strings")
        if not isinstance(deps, (list, tuple)):
            raise ValueError("dependencies must be lists or tuples")

        unique = set()
        for dep in deps:
            if not isinstance(dep, str) or not dep:
                raise ValueError("dependency IDs must be nonempty strings")
            unique.add(dep)

        dependencies[node] = unique
        nodes.add(node)
        nodes.update(unique)

    indegree = {node: 0 for node in nodes}
    dependents = {node: [] for node in nodes}

    for node, deps in dependencies.items():
        indegree[node] = len(deps)
        for dep in deps:
            dependents[dep].append(node)

    ready = [node for node in nodes if indegree[node] == 0]
    heapq.heapify(ready)
    result = []

    while ready:
        node = heapq.heappop(ready)
        result.append(node)
        for dependent in dependents[node]:
            indegree[dependent] -= 1
            if indegree[dependent] == 0:
                heapq.heappush(ready, dependent)

    if len(result) != len(nodes):
        raise ValueError("graph contains a cycle")

    return result
