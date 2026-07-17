from ...map.base import ArchitectureMap

from ..base import FlowViolation


class BaseFlowAnalyzer:
    def module_for(self, architecture_map: ArchitectureMap, source_id: str) -> str:
        module_tag = architecture_map.realm.module_tag
        if not module_tag:
            return ""

        match = architecture_map.tag_map.first_match(source_id, (module_tag,))
        if match is None:
            return ""
        return match.captured_path or match.name

    def layer_for(
        self,
        architecture_map: ArchitectureMap,
        source_id: str,
        layers: tuple[str, ...] | None = None,
    ) -> str:
        layer_names = layers or architecture_map.realm.layers
        if not layer_names:
            return ""

        match = architecture_map.tag_map.first_match(source_id, layer_names)
        if match is None:
            return ""
        return match.name

    def dedupe(self, violations: list[FlowViolation]) -> tuple[FlowViolation, ...]:
        seen: set[tuple[object, ...]] = set()
        result: list[FlowViolation] = []
        for violation in violations:
            key = violation.violation_key()
            if key in seen:
                continue
            seen.add(key)
            result.append(violation)
        return tuple(result)
