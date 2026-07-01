from __future__ import annotations

import re
from typing import Protocol

from pydantic import BaseModel


class SourceIdProvider(Protocol):
    def source_ids(self) -> tuple[str, ...]:
        raise NotImplementedError


class ArchitectureRootProvider(Protocol):
    architecture_root: str


class TagMatch(BaseModel):
    name: str
    pattern: str
    matched_path: str
    captured_path: str
    is_wildcard: bool
    wildcard_values: tuple[str, ...] = ()


class TagMap(BaseModel):
    matches_by_node: dict[str, tuple[TagMatch, ...]]

    def tags_for(self, node_id: str) -> tuple[TagMatch, ...]:
        return self.matches_by_node.get(node_id, ())

    def first_match(self, node_id: str, names: tuple[str, ...]) -> TagMatch | None:
        wanted = set(names)
        return next(
            (match for match in self.tags_for(node_id) if match.name in wanted),
            None,
        )


class TagMatcher:
    def __init__(self, config):
        self.config = config
        self.language = config.language
        self.exclusions = {
            rule.match: tuple(rule.excluded_patterns)
            for rule in getattr(config.rules, "tags", ())
        }
        self.tags = tuple(getattr(config.rules, "tags", ()))

    def match(self, node_id: str, name: str, *, scope: bool = True) -> TagMatch | None:
        matches = self.matches(node_id, name, scope=scope)
        if matches:
            return matches[0]
        if self.has_tag(name):
            return None
        pattern = name
        return self.match_pattern(
            node_id,
            pattern,
            name=name,
            scope=scope,
        )

    def matches(
        self,
        node_id: str,
        name: str,
        *,
        scope: bool = True,
    ) -> tuple[TagMatch, ...]:
        return tuple(
            match
            for tag in self.tags
            if tag.name == name
            if (match := self.match_tag_rule(node_id, tag, scope=scope)) is not None
        )

    def match_pattern(
        self,
        node_id: str,
        pattern: str,
        *,
        name: str = "",
        scope: bool = True,
        exclude: tuple[str, ...] = (),
    ) -> TagMatch | None:
        path = normalize_source_id(self.language, node_id)
        for ignored in (*self.exclusions.get(pattern, ()), *exclude):
            for normalized_ignored in normalized_patterns(self.language, ignored, self.config):
                if pattern_regex(normalized_ignored, True).match(path):
                    return None
        for normalized in normalized_patterns(self.language, pattern, self.config):
            match = pattern_regex(normalized, scope).match(path)
            if match is not None:
                return TagMatch(
                    name=name or pattern,
                    pattern=pattern,
                    matched_path=match.group(0),
                    captured_path=match.group(1),
                    is_wildcard="*" in normalized or "?" in normalized,
                    wildcard_values=tuple(match.groups()[1:]),
                )
        return None

    def first_match(
        self,
        node_id: str,
        names: tuple[str, ...],
        *,
        scope: bool = True,
    ) -> TagMatch | None:
        return next(
            (
                tag_match
                for name in names
                if (tag_match := self.match(node_id, name, scope=scope)) is not None
            ),
            None,
        )

    def tags_for(self, node_id: str) -> tuple[TagMatch, ...]:
        return tuple(
            match
            for tag in self.tags
            if (match := self.match_tag_rule(node_id, tag)) is not None
        )

    def map_code_map(self, code_map) -> TagMap:
        return TagMap(
            {
                source_id: self.tags_for(source_id)
                for source_id in source_files(code_map)
            }
        )

    def display_path(self, node_id: str) -> str:
        path = normalize_source_id(self.language, node_id)
        architecture_root = normalize_source_id(
            self.language,
            getattr(self.config, "architecture_root", "") or "",
        ).strip("/")
        if architecture_root and path.startswith(f"{architecture_root}/"):
            return path[len(architecture_root) + 1 :]
        return path

    def match_tag_rule(self, node_id: str, tag, *, scope: bool = True) -> TagMatch | None:
        return self.match_pattern(
            node_id,
            tag.match,
            name=tag.name,
            scope=scope,
            exclude=tag.excluded_patterns,
        )

    def has_tag(self, name: str) -> bool:
        return any(tag.name == name for tag in self.tags)


def source_files(code_map: SourceIdProvider) -> tuple[str, ...]:
    return code_map.source_ids()


def normalize_source_id(language: str, node_id: str) -> str:
    del language
    return node_id.replace("\\", "/").strip("/")


def normalized_patterns(
    language: str,
    pattern: str,
    config: ArchitectureRootProvider,
) -> tuple[str, ...]:
    normalized = normalize_source_id(language, pattern)
    architecture_root = normalize_source_id(
        language,
        getattr(config, "architecture_root", "") or "",
    ).strip("/")
    if architecture_root and not normalized.startswith(f"{architecture_root}/"):
        return (f"{architecture_root}/{normalized}",)
    return (normalized,)


def pattern_regex(pattern: str, scope: bool) -> re.Pattern[str]:
    parts: list[str] = []
    for character in pattern:
        if character == "*":
            parts.append("([^/]+)")
        elif character == "?":
            parts.append("([^/])")
        else:
            parts.append(re.escape(character))
    suffix = r"(?:/.*)?$" if scope else "$"
    return re.compile(rf"^({''.join(parts)}){suffix}")


__all__ = [
    "TagMap",
    "TagMatch",
    "TagMatcher",
    "normalize_source_id",
    "normalized_patterns",
    "pattern_regex",
    "source_files",
]
