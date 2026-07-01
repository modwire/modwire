from pydantic import (BaseModel, ConfigDict, Field, )


class TagRule(BaseModel):
    model_config = ConfigDict(frozen=True, from_attributes=True)

    name: str
    match: str
    excluded_patterns: tuple[str, ...] = ()


class FlowRealm(BaseModel):
    model_config = ConfigDict(frozen=True, from_attributes=True)

    name: str = ""
    module_tag: str = ""
    layers: tuple[str, ...] = ()


class FlowRules(BaseModel):
    model_config = ConfigDict(frozen=True, from_attributes=True)

    layers: tuple[str, ...] = ()
    module_tag: str = ""
    realms: tuple[FlowRealm, ...] = ()
    analyzers: tuple[str, ...] = ()


class BoundaryRule(BaseModel):
    model_config = ConfigDict(frozen=True, from_attributes=True)

    source: str
    disallow: tuple[str, ...] = ()
    allow: tuple[str, ...] = ()
    allow_same_match: bool = False


class BoundariesConfig(BaseModel):
    model_config = ConfigDict(frozen=True, from_attributes=True)

    tags: tuple[TagRule, ...] = ()
    rules: tuple[BoundaryRule, ...] = ()
    flow: FlowRules = Field(default_factory=FlowRules)
