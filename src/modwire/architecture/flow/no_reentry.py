def _no_reentry(name, graph, tags, config, realm):
    module_tag = realm.module_tag if realm is not None else config.rules.flow.module_tag
    violations = []
    seen = set()

    def walk(node, state, path):
        if (node, state) in seen:
            return
        seen.add((node, state))
        for edge in graph.outgoing(node):
            inside = module_tag in tags.get(edge.to_id, set())
            next_state = 1 if state == 0 and inside else 2 if state == 1 and not inside else state
            if state == 2 and inside:
                violations.append(_flow(name, [*path, edge.to_id], len(path), "module layer re-entered after exit", realm))
                continue
            walk(edge.to_id, next_state, [*path, edge.to_id])

    for root in _roots(graph):
        walk(root, 1 if module_tag in tags.get(root, set()) else 0, [root])
    return _dedupe(violations)
