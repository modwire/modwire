from __future__ import annotations

from collections import Counter
from dataclasses import dataclass

from modwire.extraction import CodeMap

from .matching import TagMap, TagMatcher


@dataclass(frozen=True)
class CrossModuleDependency:
    source: str
    target: str
    count: int


@dataclass(frozen=True)
class ArchitectureMap:
    tag_map: TagMap
    modules: dict[str, tuple[str, ...]]
    layers: dict[str, tuple[str, ...]]
    unknown_files: tuple[str, ...]
    cross_module_dependencies: tuple[CrossModuleDependency, ...]


@dataclass(frozen=True)
class ArchitectureCluster:
    name: str
    files: tuple[str, ...]
    incoming_count: int
    outgoing_count: int
    pressure_score: int
    top_files: tuple[str, ...]


@dataclass(frozen=True)
class DependencyHotspot:
    source_id: str
    incoming_count: int
    outgoing_count: int
    pressure_score: int


@dataclass(frozen=True)
class CoherenceSummary:
    roots: tuple[str, ...]
    leaves: tuple[str, ...]
    isolated: tuple[str, ...]
    external_dependencies: tuple[str, ...]


def map_code(code_map: CodeMap, config) -> ArchitectureMap:
    matcher = TagMatcher(config)
    tag_map = matcher.map_code_map(code_map)
    source_ids = set(code_map.extraction_result.files)
    modules = _files_by_tag(tag_map, source_ids, "module")
    layers = _files_by_tag(tag_map, source_ids, "layer")
    unknown_files = tuple(
        sorted(source_id for source_id in source_ids if not tag_map.tags_for(source_id))
    )
    return ArchitectureMap(
        tag_map=tag_map,
        modules=modules,
        layers=layers,
        unknown_files=unknown_files,
        cross_module_dependencies=_cross_module_dependencies(code_map, tag_map),
    )


def cluster_code(code_map: CodeMap, group_depth: int = 2) -> tuple[ArchitectureCluster, ...]:
    groups: dict[str, list[str]] = {}
    for source_id in code_map.extraction_result.files:
        group = "/".join(source_id.split("/")[:group_depth])
        groups.setdefault(group, []).append(source_id)

    clusters = []
    for name, files in groups.items():
        file_set = set(files)
        incoming = sum(
            1
            for edge in code_map.graph.edges
            if edge.to_id in file_set and edge.from_id not in file_set
        )
        outgoing = sum(
            1
            for edge in code_map.graph.edges
            if edge.from_id in file_set and edge.to_id not in file_set
        )
        per_file_pressure = Counter()
        for edge in code_map.graph.edges:
            if edge.from_id in file_set:
                per_file_pressure[edge.from_id] += 1
            if edge.to_id in file_set:
                per_file_pressure[edge.to_id] += 1
        clusters.append(
            ArchitectureCluster(
                name=name,
                files=tuple(sorted(files)),
                incoming_count=incoming,
                outgoing_count=outgoing,
                pressure_score=incoming + outgoing,
                top_files=tuple(
                    source_id
                    for source_id, _ in sorted(
                        per_file_pressure.items(),
                        key=lambda item: (-item[1], item[0]),
                    )[:5]
                ),
            )
        )
    return tuple(sorted(clusters, key=lambda cluster: cluster.name))


def find_hotspots(
    code_map: CodeMap,
    config="",
    limit: int = 10,
) -> tuple[DependencyHotspot, ...]:
    source_ids = set(code_map.extraction_result.files)
    hotspots = [
        DependencyHotspot(
            source_id=source_id,
            incoming_count=len(
                [
                    edge
                    for edge in code_map.graph.incoming(source_id)
                    if edge.from_id in source_ids
                ]
            ),
            outgoing_count=len(
                [
                    edge
                    for edge in code_map.graph.outgoing(source_id)
                    if edge.to_id in source_ids
                ]
            ),
            pressure_score=0,
        )
        for source_id in source_ids
    ]
    scored = [
        DependencyHotspot(
            hotspot.source_id,
            hotspot.incoming_count,
            hotspot.outgoing_count,
            hotspot.incoming_count + hotspot.outgoing_count,
        )
        for hotspot in hotspots
    ]
    return tuple(
        sorted(
            scored,
            key=lambda hotspot: (-hotspot.pressure_score, hotspot.source_id),
        )[:limit]
    )


def coherence_summary(code_map: CodeMap) -> CoherenceSummary:
    source_ids = set(code_map.extraction_result.files)
    roots = tuple(
        sorted(
            source_id
            for source_id in source_ids
            if not [
                edge
                for edge in code_map.graph.incoming(source_id)
                if edge.from_id in source_ids
            ]
        )
    )
    leaves = tuple(
        sorted(
            source_id
            for source_id in source_ids
            if not [
                edge
                for edge in code_map.graph.outgoing(source_id)
                if edge.to_id in source_ids
            ]
        )
    )
    isolated = tuple(sorted(set(roots).intersection(leaves)))
    external_dependencies = tuple(
        sorted(
            {
                edge.to_id
                for edge in code_map.graph.edges
                if edge.from_id in source_ids and edge.to_id not in source_ids
            }
        )
    )
    return CoherenceSummary(
        roots=roots,
        leaves=leaves,
        isolated=isolated,
        external_dependencies=external_dependencies,
    )


def _files_by_tag(
    tag_map: TagMap,
    source_ids: set[str],
    name: str,
) -> dict[str, tuple[str, ...]]:
    groups: dict[str, list[str]] = {}
    for source_id in source_ids:
        match = tag_map.first_match(source_id, (name,))
        if match is not None:
            groups.setdefault(match.captured_path, []).append(source_id)
    return {
        group: tuple(sorted(files))
        for group, files in sorted(groups.items())
    }


def _cross_module_dependencies(
    code_map: CodeMap,
    tag_map: TagMap,
) -> tuple[CrossModuleDependency, ...]:
    counts: Counter[tuple[str, str]] = Counter()
    for edge in code_map.tracked_edges():
        source = tag_map.first_match(edge.from_id, ("module",))
        target = tag_map.first_match(edge.to_id, ("module",))
        if source is None or target is None:
            continue
        if source.captured_path != target.captured_path:
            counts[(source.captured_path, target.captured_path)] += 1
    return tuple(
        CrossModuleDependency(source, target, count)
        for (source, target), count in sorted(counts.items())
    )


__all__ = [
    "ArchitectureCluster",
    "ArchitectureMap",
    "CoherenceSummary",
    "CrossModuleDependency",
    "DependencyHotspot",
    "cluster_code",
    "coherence_summary",
    "find_hotspots",
    "map_code",
]
