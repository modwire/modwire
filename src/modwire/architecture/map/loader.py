from typing import Annotated

from modwire_extraction.code import QueryableCodeMap
from wireup import Inject, injectable

from modwire.shared.config import ArchitectureConfig

from ..boundaries.tags import TagMatcher

from .base import ArchitectureMap, ArchitectureRealm


@injectable(lifetime="transient")
class ArchitectureMapLoader:
    def __init__(
        self,
        config: Annotated[ArchitectureConfig, Inject(config="architecture") ],
    ):
        self.config = config
        self.matcher = TagMatcher(self.config.boundaries)

    def default_realm(self) -> ArchitectureRealm:
        flow = self.config.boundaries.flow
        return ArchitectureRealm(
            name="",
            module_tag=flow.module_tag,
            layers=flow.layers,
        )

    def load(self, code_map: QueryableCodeMap) -> ArchitectureMap:
        source_ids = tuple(code_map.source_ids())
        tag_map = self.matcher.map_for(source_ids)

        return ArchitectureMap(
            code_map=code_map,
            tag_map=tag_map,
            modules=self.matcher.group_by_capture(tag_map, self.module_tags()),
            layers=self.matcher.group_by_name(tag_map, self.layer_tags()),
            unknown_files=tuple(
                source_id
                for source_id in source_ids
                if source_id not in tag_map.matches_by_node
            ),
            realm=self.default_realm(),
        )

    def module_tags(self) -> tuple[str, ...]:
        tags = [self.config.boundaries.flow.module_tag]
        tags.extend(realm.module_tag for realm in self.config.boundaries.flow.realms)
        return self.unique_non_empty(tags)

    def layer_tags(self) -> tuple[str, ...]:
        tags = [*self.config.boundaries.flow.layers]
        for realm in self.config.boundaries.flow.realms:
            tags.extend(realm.layers)
        return self.unique_non_empty(tags)

    def unique_non_empty(self, values: list[str]) -> tuple[str, ...]:
        seen: set[str] = set()
        result: list[str] = []

        for value in values:
            if value and value not in seen:
                seen.add(value)
                result.append(value)

        return tuple(result)
