from collections.abc import Callable

from modwire_extraction.code import QueryableCodeMap

from ..config import ArchitectureConfig

from .tags import TagMap, load_tag_matcher
from .tags.tag_map import TagMatch


class ArchitectureMap:
    config: ArchitectureConfig
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
    ):
        self.config = config
        self.code_map = code_map
        self.tag_map = tag_map
        self.modules = modules
        self.layers = layers
        self.unknown_files = unknown_files


def load_architecture_map(
    config: ArchitectureConfig,
    code_map: QueryableCodeMap,
) -> ArchitectureMap:
    matcher = load_tag_matcher(config)
    matches_by_node = {
        source_id: matches
        for source_id in code_map.source_ids()
        if (matches := matcher.tags_for(source_id))
    }
    tag_map = TagMap(matches_by_node=matches_by_node)

    module_tags = _module_tags(config)
    layer_tags = _layer_tags(config)

    return ArchitectureMap(
        config=config,
        code_map=code_map,
        tag_map=tag_map,
        modules=_group_by_capture(tag_map, module_tags),
        layers=_group_by_name(tag_map, layer_tags),
        unknown_files=tuple(
            source_id
            for source_id in code_map.source_ids()
            if source_id not in matches_by_node
        ),
    )


def _module_tags(config: ArchitectureConfig) -> tuple[str, ...]:
    tags = [config.boundaries.flow.module_tag]
    tags.extend(realm.module_tag for realm in config.boundaries.flow.realms)
    return _unique_non_empty(tags)


def _layer_tags(config: ArchitectureConfig) -> tuple[str, ...]:
    tags = [*config.boundaries.flow.layers]
    for realm in config.boundaries.flow.realms:
        tags.extend(realm.layers)
    return _unique_non_empty(tags)


def _unique_non_empty(values: list[str]) -> tuple[str, ...]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if not value or value in seen:
            continue
        seen.add(value)
        result.append(value)
    return tuple(result)


def _group_by_capture(
    tag_map: TagMap,
    tag_names: tuple[str, ...],
) -> dict[str, tuple[str, ...]]:
    return _group_by_tag(tag_map, tag_names, key_for_match=_captured_key)


def _group_by_name(
    tag_map: TagMap,
    tag_names: tuple[str, ...],
) -> dict[str, tuple[str, ...]]:
    return _group_by_tag(tag_map, tag_names, key_for_match=lambda match: match.name)


def _group_by_tag(
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


def _captured_key(match: TagMatch) -> str:
    if match.captured_path:
        return match.captured_path
    return match.name
