def _edge_violations(graph, config):
    violations = []
    matcher = TagMatcher(config)
    for edge in graph.edges:
        denied: tuple[str, str] = ("", "")
        for rule in config.rules.boundaries:
            source = matcher.match_pattern(edge.from_id, rule.source)
            if source is None:
                continue
            for target in rule.disallow:
                target_match = matcher.match_pattern(edge.to_id, target)
                same_owner = (
                    rule.allow_same_match
                    and source.is_wildcard
                    and target_match is not None
                    and target_match.is_wildcard
                    and source.wildcard_values == target_match.wildcard_values
                )
                if target_match is not None and not same_owner:
                    denied = (rule.source, target)
            for target in rule.allow:
                if matcher.match_pattern(
                    edge.to_id,
                    target,
                    scope=target in matcher.exclusions,
                ):
                    denied = ("", "")
        if denied[0]:
            violations.append(
                EdgeRuleViolation(
                    edge.from_id,
                    edge.to_id,
                    denied[0],
                    denied[1],
                    f"boundary:{denied[0]}->{denied[1]}:deny",
                )
            )
    return violations
