from __future__ import annotations

from dataclasses import dataclass

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    ValidationError,
    field_validator,
    model_validator,
)

from .analyzers import supported_analyzers


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


class ArchitectureFlowRules(BaseModel):
    model_config = ConfigDict(frozen=True, from_attributes=True)

    layers: tuple[str, ...] = ()
    module_tag: str = ""
    analyzers: tuple[str, ...] = ()

    @field_validator("analyzers")
    @classmethod
    def known_analyzers(cls, analyzers: tuple[str, ...]) -> tuple[str, ...]:
        unknown = tuple(
            analyzer for analyzer in analyzers if analyzer not in supported_analyzers()
        )
        if unknown:
            raise ValueError(f"Unsupported flow analyzer: {', '.join(unknown)}")
        return analyzers

    @model_validator(mode="after")
    def analyzers_have_required_config(self) -> ArchitectureFlowRules:
        if "backward-flow" in self.analyzers and not self.layers:
            raise ValueError("backward-flow requires rules.flow.layers")
        scoped_analyzers = {"no-reentry", "no-cycles"}.intersection(self.analyzers)
        if scoped_analyzers and not self.module_tag:
            names = ", ".join(sorted(scoped_analyzers))
            raise ValueError(f"{names} require rules.flow.module_tag")
        return self


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


@dataclass(frozen=True)
class ArchitectureConfigIssue:
    field: str
    message: str

    def to_dict(self) -> dict[str, str]:
        return {
            "field": self.field,
            "message": self.message,
        }


class ArchitectureConfigError(ValueError):
    def __init__(self, issues: tuple[ArchitectureConfigIssue, ...]):
        self.issues = issues
        super().__init__("Invalid architecture config")

    def to_dict(self) -> dict[str, object]:
        return {
            "error": "invalid_architecture_config",
            "issues": [issue.to_dict() for issue in self.issues],
        }


def validate_policy_config(config) -> ArchitectureConfig:
    try:
        return ArchitectureConfig.model_validate(config)
    except ValidationError as error:
        raise ArchitectureConfigError(
            tuple(
                ArchitectureConfigIssue(
                    field=".".join(str(part) for part in issue["loc"]),
                    message=str(issue["msg"]),
                )
                for issue in error.errors()
            )
        ) from error


__all__ = [
    "ArchitectureBoundaryRule",
    "ArchitectureConfig",
    "ArchitectureConfigError",
    "ArchitectureConfigIssue",
    "ArchitectureFlowRules",
    "ArchitectureRules",
    "ArchitectureTagRule",
    "validate_policy_config",
]
