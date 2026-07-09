from pydantic import Field

from .base import ModwireBaseConfig
from .shape import ShapeConfig


class TagRule(ModwireBaseConfig):
    name: str
    match: str
    excluded_patterns: tuple[str, ...] = ()


class FlowRealm(ModwireBaseConfig):
    name: str = ""
    module_tag: str = ""
    layers: tuple[str, ...] = ()


class FlowRules(ModwireBaseConfig):
    layers: tuple[str, ...] = ()
    module_tag: str = ""
    realms: tuple[FlowRealm, ...] = ()
    analyzers: tuple[str, ...] = ()


class BoundaryRule(ModwireBaseConfig):
    source: str
    disallow: tuple[str, ...] = ()
    allow: tuple[str, ...] = ()
    allow_same_match: bool = False


class BoundariesConfig(ModwireBaseConfig):
    tags: tuple[TagRule, ...] = ()
    rules: tuple[BoundaryRule, ...] = ()
    flow: FlowRules = Field(default_factory=FlowRules)


class ArchitectureConfig(ModwireBaseConfig):
    boundaries: BoundariesConfig = Field(default_factory=BoundariesConfig)
    shape: ShapeConfig = Field(default_factory=ShapeConfig)
