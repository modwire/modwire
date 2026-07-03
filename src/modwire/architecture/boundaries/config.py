from pydantic import Field

from modwire.shared import ModwireConfig


class TagRule(ModwireConfig):
    name: str
    match: str
    excluded_patterns: tuple[str, ...] = ()


class FlowRealm(ModwireConfig):
    name: str = ""
    module_tag: str = ""
    layers: tuple[str, ...] = ()


class FlowRules(ModwireConfig):
    layers: tuple[str, ...] = ()
    module_tag: str = ""
    realms: tuple[FlowRealm, ...] = ()
    analyzers: tuple[str, ...] = ()


class BoundaryRule(ModwireConfig):
    source: str
    disallow: tuple[str, ...] = ()
    allow: tuple[str, ...] = ()
    allow_same_match: bool = False


class BoundariesConfig(ModwireConfig):
    tags: tuple[TagRule, ...] = ()
    rules: tuple[BoundaryRule, ...] = ()
    flow: FlowRules = Field(default_factory=FlowRules)
