from ...config import ArchitectureConfig
from .tag_map import TagMatch


class TagMatcher:
    def __init__(self, config: ArchitectureConfig):
        self.language = config.language
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
        pass

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


def load_tag_matcher(config: ArchitectureConfig) -> TagMatcher:
    return TagMatcher(config)