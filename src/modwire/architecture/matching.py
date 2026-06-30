from pydantic import BaseModel


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

