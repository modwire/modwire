from __future__ import annotations

import re
from dataclasses import dataclass
from functools import cache

from modwire._code_map import source_files


@dataclass(frozen=True)
class TagMatch:
    name: str
    pattern: str
    matched_path: str
    captured_path: str
    is_wildcard: bool
    wildcard_values: tuple[str, ...] = ()


@dataclass(frozen=True)
class TagMap:
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
        if self._has_tag(name):
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
            if (match := self._match_tag(node_id, tag, scope=scope)) is not None
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
            for normalized_ignored in _normalized_patterns(self.language, ignored, self.config):
                if _regex(normalized_ignored, True).match(path):
                    return None
        for normalized in _normalized_patterns(self.language, pattern, self.config):
            match = _regex(normalized, scope).match(path)
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
            if (match := self._match_tag(node_id, tag)) is not None
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

    def _match_tag(self, node_id: str, tag, *, scope: bool = True) -> TagMatch | None:
        return self.match_pattern(
            node_id,
            tag.match,
            name=tag.name,
            scope=scope,
            exclude=tag.excluded_patterns,
        )

    def _has_tag(self, name: str) -> bool:
        return any(tag.name == name for tag in self.tags)


def _normalized_patterns(language, pattern, config):
    normalized = normalize_source_id(language, pattern).strip("/")
    architecture_root = normalize_source_id(
        language,
        getattr(config, "architecture_root", None) or "",
    ).strip("/")
    if not architecture_root:
        return (normalized,)

    root_anchor = architecture_root.split("/", 1)[0]
    is_full_path = normalized == architecture_root or normalized.startswith(
        (f"{architecture_root}/", f"{root_anchor}/")
    )
    if is_full_path:
        return (normalized,)
    return (f"{architecture_root}/{normalized}",)


def normalize_source_id(language: str, value: str) -> str:
    del language
    normalized = value.replace("\\", "/").strip().strip("/")
    if not normalized:
        return ""
    parts = normalized.split("/")
    if "." in parts[-1] and not any(char in parts[-1] for char in "*?"):
        parts[-1] = parts[-1].rsplit(".", 1)[0]
    return "/".join(parts)


@cache
def _regex(pattern: str, scope: bool):
    parts = ["^("]
    i = 0
    while i < len(pattern):
        char = pattern[i]
        if char == "*":
            is_deep = i + 1 < len(pattern) and pattern[i + 1] == "*"
            parts.append("(.*)" if is_deep else "([^/]*)")
            i += 2 if is_deep else 1
        elif char == "?":
            parts.append("([^/])")
            i += 1
        else:
            parts.append(re.escape(char))
            i += 1
    parts.append(")(?:/.*)?" if scope else ")")
    return re.compile("".join(parts) + "$")
