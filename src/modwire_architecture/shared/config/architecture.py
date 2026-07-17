from pydantic import Field, field_validator, model_validator

from ..base import ModwireConfigModel
from .shape import ShapeConfig


class TagRule(ModwireConfigModel):
    name: str
    match: str
    excluded_patterns: tuple[str, ...] = ()

    @field_validator("name", "match")
    @classmethod
    def require_value(cls, value: str) -> str:
        if not value:
            raise ValueError("Tag name and match pattern cannot be empty")
        return value


class FlowRealm(ModwireConfigModel):
    name: str = ""
    module_tag: str = ""
    layers: tuple[str, ...] = ()


class FlowRules(ModwireConfigModel):
    layers: tuple[str, ...] = ()
    module_tag: str = ""
    realms: tuple[FlowRealm, ...] = ()
    analyzers: tuple[str, ...] = ()

    @model_validator(mode="after")
    def unique_realms(self) -> "FlowRules":
        names = tuple(realm.name for realm in self.realms if realm.name)
        if len(names) != len(set(names)):
            raise ValueError("Flow realm names must be unique")
        if len(self.analyzers) != len(set(self.analyzers)):
            raise ValueError("Flow analyzer names must be unique")
        return self


class BoundaryRule(ModwireConfigModel):
    source: str
    disallow: tuple[str, ...] = ()
    allow: tuple[str, ...] = ()
    allow_same_match: bool = False


class BoundariesConfig(ModwireConfigModel):
    tags: tuple[TagRule, ...] = ()
    rules: tuple[BoundaryRule, ...] = ()
    flow: FlowRules = Field(default_factory=FlowRules)

    @model_validator(mode="after")
    def unique_tag_names(self) -> "BoundariesConfig":
        names = tuple(tag.name for tag in self.tags)
        duplicates = sorted({name for name in names if names.count(name) > 1})
        if duplicates:
            raise ValueError(
                "Architecture tag names must be unique: " + ", ".join(duplicates)
            )
        return self


class ArchitectureConfig(ModwireConfigModel):
    boundaries: BoundariesConfig = Field(default_factory=BoundariesConfig)
    shape: ShapeConfig = Field(default_factory=ShapeConfig)
