import heapq


def schedule(graph):
    if not isinstance(graph, dict):
        raise ValueError("graph must be a dict")

    nodes = set()
    dependencies = {}

    for node, raw_dependencies in graph.items():
        if not isinstance(node, str) or not node:
            raise ValueError("node IDs must be nonempty strings")
        if not isinstance(raw_dependencies, (list, tuple)):
            raise ValueError("dependencies must be lists or tuples")

        unique_dependencies = set()
        for dependency in raw_dependencies:
            if not isinstance(dependency, str) or not dependency:
                raise ValueError("dependency IDs must be nonempty strings")
            unique_dependencies.add(dependency)

        nodes.add(node)
        nodes.update(unique_dependencies)
        dependencies[node] = unique_dependencies

    dependents = {node: [] for node in nodes}
    indegree = {node: 0 for node in nodes}

    for node, node_dependencies in dependencies.items():
        indegree[node] = len(node_dependencies)
        for dependency in node_dependencies:
            dependents[dependency].append(node)

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
