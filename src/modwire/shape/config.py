from __future__ import annotations

from dataclasses import dataclass

from pydantic import BaseModel, ConfigDict, ValidationError, field_validator

from ..definitions import ImportCrossingType


class ShapeConfig(BaseModel):
    model_config = ConfigDict(frozen=True)

    max_classes_per_file: int = -1
    max_interfaces_per_file: int = -1
    max_types_per_file: int = -1
    max_abstract_classes_per_file: int = -1
    max_functions_per_file: int = -1
    max_methods_per_class: int = -1
    max_declared_args: int = -1
    max_function_lines: int = -1
    max_method_lines: int = -1
    max_class_lines: int = -1
    allow_optional_function_args: bool = True
    allow_optional_method_args: bool = True
    allow_optional_class_properties: bool = True
    allow_import_aliases: bool = True
    allowed_import_crossing_types: tuple[ImportCrossingType, ...] = ("module", "symbol")
    require_joined_imports: bool = False

    @field_validator(
        "max_classes_per_file",
        "max_interfaces_per_file",
        "max_types_per_file",
        "max_abstract_classes_per_file",
        "max_functions_per_file",
        "max_methods_per_class",
        "max_declared_args",
        "max_function_lines",
        "max_method_lines",
        "max_class_lines",
    )
    @classmethod
    def disabled_or_non_negative(cls, limit: int) -> int:
        if limit < -1:
            raise ValueError("Limit must be -1 or a non-negative integer")
        return limit


@dataclass(frozen=True)
class ShapeConfigIssue:
    field: str
    message: str

    def to_dict(self) -> dict[str, str]:
        return {
            "field": self.field,
            "message": self.message,
        }


class ShapeConfigError(ValueError):
    def __init__(self, issues: tuple[ShapeConfigIssue, ...]):
        self.issues = issues
        super().__init__("Invalid shape config")

    def to_dict(self) -> dict[str, object]:
        return {
            "error": "invalid_shape_config",
            "issues": [issue.to_dict() for issue in self.issues],
        }


def validate_shape_config(config) -> ShapeConfig:
    try:
        return ShapeConfig.model_validate(config)
    except ValidationError as error:
        raise ShapeConfigError(
            tuple(
                ShapeConfigIssue(
                    field=".".join(str(part) for part in issue["loc"]),
                    message=str(issue["msg"]),
                )
                for issue in error.errors()
            )
        ) from error


__all__ = [
    "ShapeConfig",
    "ShapeConfigError",
    "ShapeConfigIssue",
    "validate_shape_config",
]
