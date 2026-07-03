from pydantic import field_validator

from modwire.shared import ModwireConfig


class ShapeConfig(ModwireConfig):
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
    allow_import_aliases: bool = False
    allowed_import_crossing_types: tuple[str, ...] = ("module",)
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
