import heapq


def schedule(graph):
    if not isinstance(graph, dict):
        raise ValueError

    nodes = set()
    dependencies = {}

    for node, deps in graph.items():
        if not isinstance(node, str) or not node:
            raise ValueError
        if not isinstance(deps, (list, tuple)):
            raise ValueError

        nodes.add(node)
        unique_deps = set()
        for dep in deps:
            if not isinstance(dep, str) or not dep:
                raise ValueError
            unique_deps.add(dep)

        dependencies[node] = unique_deps
        nodes.update(unique_deps)

    outgoing = {node: set() for node in nodes}
    indegree = {node: 0 for node in nodes}

    for node, deps in dependencies.items():
        for dep in deps:
            outgoing[dep].add(node)
            indegree[node] += 1

    ready = [node for node in nodes if indegree[node] == 0]
    heapq.heapify(ready)
    result = []

    while ready:
        node = heapq.heappop(ready)
        result.append(node)

        for dependent in outgoing[node]:
            indegree[dependent] -= 1
            if indegree[dependent] == 0:
                heapq.heappush(ready, dependent)

    if len(result) != len(nodes):
        raise ValueError

    return result
