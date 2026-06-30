def _no_cycles(name, graph, tags, config, realm):
    module_tag = realm.module_tag if realm is not None else config.rules.flow.module_tag
    scoped = {node for node, node_tags in tags.items() if module_tag in node_tags}
    seen, stack, index, emitted, violations = set(), [], {}, set(), []

    def canonical(cycle):
        ring = list(cycle[:-1])
        first = min(tuple(ring[i:] + ring[:i]) for i in range(len(ring)))
        return (*first, first[0])

    def dfs(node):
        seen.add(node)
        index[node] = len(stack)
        stack.append(node)
        for edge in graph.outgoing(node):
            if edge.to_id not in scoped:
                continue
            if edge.to_id in index:
                cycle = tuple([*stack[index[edge.to_id] :], edge.to_id])
                key = canonical(cycle)
                if key not in emitted:
                    emitted.add(key)
                    violations.append(_flow(name, cycle, len(cycle) - 1, "module cycle detected", realm))
            elif edge.to_id not in seen:
                dfs(edge.to_id)
        stack.pop()
        index.pop(node, None)

    for node in sorted(scoped):
        if node not in seen:
            dfs(node)
    return violations