import re

from ...config import ArchitectureConfig
from .tag_map import TagMatch


class TagMatcher:
    def __init__(self, config: ArchitectureConfig):
        self.language = config.language
        self.root = config.root
        self.boundaries = config.boundaries
        self.tags = self.boundaries.tags

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
        normalized_node = self.normalize_path(node_id)
        normalized_pattern = self.normalize_path(pattern)
        if any(
            self.match_pattern(node_id, excluded, scope=scope) is not None
            for excluded in exclude
        ):
            return None

        regex = self.compile_pattern(normalized_pattern, scope=scope)
        match = regex.match(normalized_node)
        if match is None:
            return None

        wildcard_values = tuple(
            value
            for value in match.groups()
            if value is not None
        )
        return TagMatch(
            name=name or pattern,
            pattern=pattern,
            matched_path=match.group(0).strip("/"),
            captured_path="/".join(wildcard_values),
            is_wildcard=bool(wildcard_values),
            wildcard_values=wildcard_values,
        )

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

    def normalize_path(self, value: str) -> str:
        normalized = value.replace("\\", "/").strip("/")
        root = self.normalize_root()
        if root and normalized.startswith(f"{root}/"):
            return normalized.removeprefix(f"{root}/")
        return normalized

    def normalize_root(self) -> str:
        return self.root.replace("\\", "/").strip("/")

    def compile_pattern(self, pattern: str, *, scope: bool) -> re.Pattern[str]:
        parts = pattern.split("/")
        pattern_regex = "/".join(
            "([^/]+)" if part == "*" else re.escape(part)
            for part in parts
        )
        if scope:
            return re.compile(f"^{pattern_regex}(?:/.*)?$")
        return re.compile(f"(?:^|.*/){pattern_regex}(?:/.*)?$")


def load_tag_matcher(config: ArchitectureConfig) -> TagMatcher:
    return TagMatcher(config)
