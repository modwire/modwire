from __future__ import annotations

from ..base import FlowAnalysisContext, FlowAnalyzer, FlowViolation


class NoReentryFlowAnalyzer(FlowAnalyzer):
    name: str = "no-reentry"
    title: str = "No Re-Entry Violations"

    def analyze(self, context: FlowAnalysisContext) -> tuple[FlowViolation, ...]:
        if not context.realm.module_tag:
            return ()

        violations: list[FlowViolation] = []
        for root in self.roots(context):
            self.walk_dependencies(
                context=context,
                source_id=root,
                path=(root,),
                exited_modules=frozenset(),
                violations=violations,
            )
        return self.dedupe(violations)

    def roots(self, context: FlowAnalysisContext) -> tuple[str, ...]:
        roots = tuple(
            source_id
            for source_id in context.code_map.source_ids()
            if context.code_map.incoming_dependencies(source_id).count() == 0
        )
        if roots:
            return roots
        return context.code_map.source_ids()

    def walk_dependencies(
        self,
        context: FlowAnalysisContext,
        source_id: str,
        path: tuple[str, ...],
        exited_modules: frozenset[str],
        violations: list[FlowViolation],
    ) -> None:
        source_module = self.module_for(context, source_id)
        for dependency in context.code_map.outgoing_dependencies(source_id).all():
            target_id = dependency.edge.to_id
            target_module = self.module_for(context, target_id)
            next_exited = exited_modules
            if source_module and target_module and source_module != target_module:
                next_exited = exited_modules.union((source_module,))

            if target_module and target_module in exited_modules:
                violations.append(
                    FlowViolation(
                        violation_type=self.name,
                        path=(*path, target_id),
                        violation_index=len(path),
                        rule_name=self.rule_name(context),
                        message="module layer re-entered after exit",
                    )
                )
                continue

            if target_id not in path:
                self.walk_dependencies(
                    context=context,
                    source_id=target_id,
                    path=(*path, target_id),
                    exited_modules=next_exited,
                    violations=violations,
                )


__all__ = ["NoReentryFlowAnalyzer"]
