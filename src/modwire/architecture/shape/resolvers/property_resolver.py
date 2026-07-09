from collections.abc import Sequence

from wireup import injectable

from ..base import (
    ArchitectureMapQuery,
    BaseShapeResolver,
    PropertyShape,
    ShapeViolation,
    SymbolShapeResolverInterface,
)
from modwire.shared.config import ShapeConfig


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
        architecture_map: ArchitectureMapQuery,
        config: ShapeConfig,
    ) -> tuple[ShapeViolation, ...]:
        if config.allow_optional_class_properties:
            return ()

        violations: list[ShapeViolation] = []
        for class_result in architecture_map.code_map.classes().all():
            source_class = class_result.item
            violations.extend(
                self.property_violations(
                    source_id=class_result.source_id,
                    symbol_kind="class_property",
                    symbol_name=getattr(source_class, "name", ""),
                    properties=getattr(source_class, "properties", ()),
                )
            )
        for interface_result in architecture_map.code_map.interfaces().all():
            source_interface = interface_result.item
            violations.extend(
                self.property_violations(
                    source_id=interface_result.source_id,
                    symbol_kind="interface_property",
                    symbol_name=getattr(source_interface, "name", ""),
                    properties=getattr(source_interface, "properties", ()),
                )
            )
        for type_result in architecture_map.code_map.types().all():
            source_type = type_result.item
            violations.extend(
                self.property_violations(
                    source_id=type_result.source_id,
                    symbol_kind="type_property",
                    symbol_name=getattr(source_type, "name", ""),
                    properties=getattr(source_type, "properties", ()),
                )
            )
        for abstract_class_result in architecture_map.code_map.abstract_classes().all():
            abstract_class = abstract_class_result.item
            violations.extend(
                self.property_violations(
                    source_id=abstract_class_result.source_id,
                    symbol_kind="abstract_class_property",
                    symbol_name=getattr(abstract_class, "name", ""),
                    properties=getattr(abstract_class, "properties", ()),
                )
            )
        return tuple(violations)

    def property_violations(
        self,
        *,
        source_id: str,
        symbol_kind: str,
        symbol_name: str,
        properties: Sequence[PropertyShape],
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
