from modwire_extraction.code import QueryableCodeMap

from modwire.shared.config import FlowRealm
from ..boundaries.tags import TagMap


class ArchitectureCodeQueries:
    def __init__(
        self,
        code_map: QueryableCodeMap,
        tag_map: TagMap,
        realm: FlowRealm,
    ):
        self._code_map = code_map
        self._tag_map = tag_map
        self._realm = realm

    def source_ids(self) -> tuple[str, ...]:
        return self._code_map.source_ids()

    def source_files(self):
        return tuple(self._code_map.source_files().all())

    def dependency_edges(self):
        return tuple(self._code_map.dependency_edges().all())

    def tracked_dependency_edges(self):
        return tuple(self._code_map.tracked_dependency_edges().all())

    def outgoing_dependencies(self, source_id: str):
        return tuple(self._code_map.outgoing_dependencies(source_id).all())

    def incoming_count(self, source_id: str) -> int:
        return self._code_map.incoming_dependencies(source_id).count()

    def outgoing_count(self, source_id: str) -> int:
        return self._code_map.outgoing_dependencies(source_id).count()

    def pressure(self, source_id: str) -> int:
        return self.incoming_count(source_id) + self.outgoing_count(source_id)

    def roots(self) -> tuple[str, ...]:
        roots = tuple(
            source_id
            for source_id in self.source_ids()
            if self.incoming_count(source_id) == 0
        )
        return roots or self.source_ids()

    def module_for(self, source_id: str) -> str:
        if not self._realm.module_tag:
            return ""
        match = self._tag_map.first_match(source_id, (self._realm.module_tag,))
        return "" if match is None else match.captured_path or match.name

    def layer_for(self, source_id: str, layers: tuple[str, ...] | None = None) -> str:
        layer_names = layers or self._realm.layers
        if not layer_names:
            return ""
        match = self._tag_map.first_match(source_id, layer_names)
        return "" if match is None else match.name
