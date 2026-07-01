from pathlib import Path

from pydantic import (BaseModel, ConfigDict, Field, )


from modwire_extraction.code import QueryableCodeMap
from modwire_extraction import ModwireExtraction


from .matching import TagMap


class ArchitectureTagRule(BaseModel):
    model_config = ConfigDict(frozen=True, from_attributes=True)

    name: str
    match: str
    excluded_patterns: tuple[str, ...] = ()


class ArchitectureBoundaryRule(BaseModel):
    model_config = ConfigDict(frozen=True, from_attributes=True)

    source: str
    disallow: tuple[str, ...] = ()
    allow: tuple[str, ...] = ()
    allow_same_match: bool = False


class ArchitectureFlowRealm(BaseModel):
    model_config = ConfigDict(frozen=True, from_attributes=True)

    name: str = ""
    module_tag: str = ""
    layers: tuple[str, ...] = ()


class ArchitectureFlowRules(BaseModel):
    model_config = ConfigDict(frozen=True, from_attributes=True)

    layers: tuple[str, ...] = ()
    module_tag: str = ""
    realms: tuple[ArchitectureFlowRealm, ...] = ()
    analyzers: tuple[str, ...] = ()


class ArchitectureRules(BaseModel):
    model_config = ConfigDict(frozen=True, from_attributes=True)

    tags: tuple[ArchitectureTagRule, ...] = ()
    boundaries: tuple[ArchitectureBoundaryRule, ...] = ()
    flow: ArchitectureFlowRules = Field(default_factory=ArchitectureFlowRules)


class ArchitectureConfig(BaseModel):
    model_config = ConfigDict(frozen=True, from_attributes=True)

    language: str
    architecture_root: str = ""
    rules: ArchitectureRules = Field(default_factory=ArchitectureRules)


class ArchitectureMap:
    tag_map: TagMap
    modules: dict[str, tuple[str, ...]]
    layers: dict[str, tuple[str, ...]]
    unknown_files: tuple[str, ...]



def flow_realms(flow: ArchitectureFlowRules) -> tuple[ArchitectureFlowRealm, ...]:
    if flow.realms:
        return flow.realms
    return (
        ArchitectureFlowRealm(
            module_tag=flow.module_tag,
            layers=flow.layers,
        ),
    )


def extract_code_map(root_path: Path, language: str) -> QueryableCodeMap:
    return ModwireExtraction(root_path).generate_queryable_map(language)
