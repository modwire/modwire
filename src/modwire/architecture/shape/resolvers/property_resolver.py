from modwire_extraction.extractors.source import SourceClassProperty, SourceFile
from wireup import injectable

from ..base import BaseShapeResolver, ShapeViolation, SymbolShapeResolverInterface
from ....shared.config.shape import ShapeConfig


@injectable(qualifier="property", as_type=SymbolShapeResolverInterface)
class PropertyResolver(SymbolShapeResolverInterface, BaseShapeResolver):
    @property
    def name(self) -> str:
        return "property"

    @property
    def title(self) -> str:
        return "Property Shape"

    def resolve(
        self,
        source_id: str,
        source_file: SourceFile,
        config: ShapeConfig,
    ) -> tuple[ShapeViolation, ...]:
        if config.allow_optional_class_properties:
            return ()

        violations: list[ShapeViolation] = []
        for source_class in source_file.classes:
            violations.extend(
                self.property_violations(
                    source_id=source_id,
                    symbol_kind="class_property",
                    symbol_name=source_class.name,
                    properties=source_class.properties,
                )
            )
        for source_interface in source_file.interfaces:
            violations.extend(
                self.property_violations(
                    source_id=source_id,
                    symbol_kind="interface_property",
                    symbol_name=source_interface.name,
                    properties=source_interface.properties,
                )
            )
        for source_type in source_file.types:
            violations.extend(
                self.property_violations(
                    source_id=source_id,
                    symbol_kind="type_property",
                    symbol_name=source_type.name,
                    properties=source_type.properties,
                )
            )
        for abstract_class in source_file.abstract_classes:
            violations.extend(
                self.property_violations(
                    source_id=source_id,
                    symbol_kind="abstract_class_property",
                    symbol_name=abstract_class.name,
                    properties=abstract_class.properties,
                )
            )
        return tuple(violations)

    def property_violations(
        self,
        *,
        source_id: str,
        symbol_kind: str,
        symbol_name: str,
        properties: list[SourceClassProperty],
    ) -> tuple[ShapeViolation, ...]:
        return tuple(
            ShapeViolation(
                source_id=source_id,
                rule_name="allow_optional_class_properties",
                actual=True,
                limit=False,
                symbol_kind=symbol_kind,
                symbol_name=property_.name or symbol_name,
            )
            for property_ in properties
            if property_.is_optional
        )
