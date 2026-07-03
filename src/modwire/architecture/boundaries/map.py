from collections.abc import Callable

from modwire_extraction.code import QueryableCodeMap

from ..config import ArchitectureConfig

from .config import FlowRealm
from .tags import TagMatcher, TagMatch, TagMap


class ArchitectureMap:
    config: ArchitectureConfig
    realm: FlowRealm
    code_map: QueryableCodeMap
    tag_map: TagMap
    modules: dict[str, tuple[str, ...]]
    layers: dict[str, tuple[str, ...]]
    unknown_files: tuple[str, ...]

    def __init__(
        self,
        config: ArchitectureConfig,
        code_map: QueryableCodeMap,
        tag_map: TagMap,
        modules: dict[str, tuple[str, ...]],
        layers: dict[str, tuple[str, ...]],
        unknown_files: tuple[str, ...],
        realm: FlowRealm | None = None,
    ):
        self.config = config
        self.realm = realm or FlowRealm(
            module_tag=config.boundaries.flow.module_tag,
            layers=config.boundaries.flow.layers,
        )
        self.code_map = code_map
        self.tag_map = tag_map
        self.modules = modules
        self.layers = layers
        self.unknown_files = unknown_files

    def with_realm(self, realm: FlowRealm) -> "ArchitectureMap":
        return ArchitectureMap(
            config=self.config,
            code_map=self.code_map,
            tag_map=self.tag_map,
            modules=self.modules,
            layers=self.layers,
            unknown_files=self.unknown_files,
            realm=realm,
        )


class ArchitectureMapLoader:
    config: ArchitectureConfig
    matcher: TagMatcher

    def __init__(self, config: ArchitectureConfig):
        self.config = config
        self.matcher = TagMatcher(config)

    def load(self, code_map: QueryableCodeMap) -> ArchitectureMap:
        matches_by_node = self.matches_by_node(code_map)
        tag_map = TagMap(matches_by_node=matches_by_node)

        return ArchitectureMap(
            config=self.config,
            code_map=code_map,
            tag_map=tag_map,
            modules=self.group_by_capture(tag_map, self.module_tags()),
            layers=self.group_by_name(tag_map, self.layer_tags()),
            unknown_files=tuple(
                source_id
                for source_id in code_map.source_ids()
                if source_id not in matches_by_node
            ),
        )

    def matches_by_node(
        self,
        code_map: QueryableCodeMap,
    ) -> dict[str, tuple[TagMatch, ...]]:
        return {
            source_id: matches
            for source_id in code_map.source_ids()
            if (matches := self.matcher.tags_for(source_id))
        }

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
            if not value or value in seen:
                continue
            seen.add(value)
            result.append(value)
        return tuple(result)

    def group_by_capture(
        self,
        tag_map: TagMap,
        tag_names: tuple[str, ...],
    ) -> dict[str, tuple[str, ...]]:
        return self.group_by_tag(tag_map, tag_names, key_for_match=self.captured_key)

    def group_by_name(
        self,
        tag_map: TagMap,
        tag_names: tuple[str, ...],
    ) -> dict[str, tuple[str, ...]]:
        return self.group_by_tag(
            tag_map,
            tag_names,
            key_for_match=lambda match: match.name,
        )

    def group_by_tag(
        self,
        tag_map: TagMap,
        tag_names: tuple[str, ...],
        *,
        key_for_match: Callable[[TagMatch], str],
    ) -> dict[str, tuple[str, ...]]:
        if not tag_names:
            return {}

        grouped: dict[str, list[str]] = {}
        wanted = set(tag_names)
        for source_id, matches in tag_map.matches_by_node.items():
            for match in matches:
                if match.name not in wanted:
                    continue
                grouped.setdefault(key_for_match(match), []).append(source_id)

        return {
            key: tuple(sorted(source_ids))
            for key, source_ids in sorted(grouped.items())
        }

    def captured_key(self, match: TagMatch) -> str:
        if match.captured_path:
            return match.captured_path
        return match.name
