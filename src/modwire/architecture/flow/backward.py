from __future__ import annotations

from .base import FlowAnalysisContext, FlowAnalyzer, FlowViolation


class BackwardFlowAnalyzer(FlowAnalyzer):
    name: str = "backward-flow"
    title: str = "Backward Flow Violations"

    def analyze(self, context: FlowAnalysisContext) -> tuple[FlowViolation, ...]:
        layers = context.realm.layers
        if not layers:
            return ()

        layer_index = {layer: index for index, layer in enumerate(layers)}
        violations: list[FlowViolation] = []
        for dependency in context.code_map.dependency_edges().all():
            source_id = dependency.edge.from_id
            target_id = dependency.edge.to_id
            source_layer = self.layer_for(context, source_id, layers)
            target_layer = self.layer_for(context, target_id, layers)
            if not source_layer or not target_layer:
                continue
            if layer_index[source_layer] > layer_index[target_layer]:
                violations.append(
                    FlowViolation(
                        violation_type=self.name,
                        path=(source_id, target_id),
                        violation_index=1,
                        rule_name=self.rule_name(context),
                        message=f"{source_id} points backward to {target_id}",
                    )
                )
        return self.dedupe(violations)
