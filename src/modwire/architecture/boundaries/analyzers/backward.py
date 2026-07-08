from wireup import injectable

from ...map.map import ArchitectureMap
from ..base import FlowViolation, FlowAnalyzerInterface
from .analyzer_base import BaseFlowAnalyzer


@injectable(qualifier="backward-flow", as_type=FlowAnalyzerInterface)
class BackwardFlowAnalyzer(FlowAnalyzerInterface, BaseFlowAnalyzer):
    @property
    def name(self) -> str:
        return "backward-flow"

    @property
    def title(self) -> str:
        return "Backward Flow Violations"

    def analyze(self, architecture_map: ArchitectureMap) -> tuple[FlowViolation, ...]:
        layers = architecture_map.realm.layers
        if not layers:
            return ()

        layer_index = {layer: index for index, layer in enumerate(layers)}
        violations: list[FlowViolation] = []
        for dependency in architecture_map.code_map.dependency_edges().all():
            source_id = dependency.edge.from_id
            target_id = dependency.edge.to_id
            source_layer = self.layer_for(architecture_map, source_id, layers)
            target_layer = self.layer_for(architecture_map, target_id, layers)
            if not source_layer or not target_layer:
                continue
            if layer_index[source_layer] > layer_index[target_layer]:
                violations.append(
                    FlowViolation(
                        violation_type=self.name,
                        path=(source_id, target_id),
                        violation_index=1,
                        rule_name=self.rule_name(architecture_map),
                        message=f"{source_id} points backward to {target_id}",
                    )
                )
        return self.dedupe(violations)
