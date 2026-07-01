from __future__ import annotations

from ..base import FlowAnalysisContext, FlowAnalyzer, FlowViolation


class NoCyclesFlowAnalyzer(FlowAnalyzer):
    name: str = "no-cycles"
    title: str = "Cycle Violations"

    def analyze(self, context: FlowAnalysisContext) -> tuple[FlowViolation, ...]:
        if not context.realm.module_tag:
            return ()

        adjacency = self.module_adjacency(context)
        emitted: set[tuple[str, ...]] = set()
        violations: list[FlowViolation] = []
        for module in sorted(adjacency):
            self.walk_modules(
                context=context,
                adjacency=adjacency,
                module=module,
                path=(module,),
                emitted=emitted,
                violations=violations,
            )
        return tuple(violations)

    def module_adjacency(
        self,
        context: FlowAnalysisContext,
    ) -> dict[str, set[str]]:
        adjacency: dict[str, set[str]] = {}
        for dependency in context.code_map.dependency_edges().all():
            source = self.module_for(context, dependency.edge.from_id)
            target = self.module_for(context, dependency.edge.to_id)
            if not source or not target or source == target:
                continue
            adjacency.setdefault(source, set()).add(target)
        return adjacency

    def walk_modules(
        self,
        context: FlowAnalysisContext,
        adjacency: dict[str, set[str]],
        module: str,
        path: tuple[str, ...],
        emitted: set[tuple[str, ...]],
        violations: list[FlowViolation],
    ) -> None:
        for target in sorted(adjacency.get(module, ())):
            if target in path:
                cycle = (*path[path.index(target) :], target)
                canonical = self.canonical_cycle(cycle)
                if canonical in emitted:
                    continue
                emitted.add(canonical)
                violations.append(
                    FlowViolation(
                        violation_type=self.name,
                        path=canonical,
                        violation_index=len(canonical) - 1,
                        rule_name=self.rule_name(context),
                        message="module cycle detected",
                    )
                )
                continue

            self.walk_modules(
                context=context,
                adjacency=adjacency,
                module=target,
                path=(*path, target),
                emitted=emitted,
                violations=violations,
            )

    def canonical_cycle(self, cycle: tuple[str, ...]) -> tuple[str, ...]:
        ring = cycle[:-1]
        rotations = tuple(
            ring[index:] + ring[:index]
            for index in range(len(ring))
        )
        first = min(rotations)
        return (*first, first[0])


__all__ = ["NoCyclesFlowAnalyzer"]
