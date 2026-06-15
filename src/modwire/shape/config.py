from __future__ import annotations

from pydantic import BaseModel, ConfigDict

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
