from modwire.shared.config import ArchitectureConfig


def standard_shape_report_collector(config: ArchitectureConfig):
    from .collector import ShapeReportCollector
    from .resolvers.abstract_class_resolver import AbstractClassResolver
    from .resolvers.callable_resolver import CallableResolver
    from .resolvers.class_resolver import ClassResolver
    from .resolvers.file_resolver import FileResolver
    from .resolvers.import_resolver import ImportResolver
    from .resolvers.property_resolver import PropertyResolver
    from .resolvers.signature_resolver import SignatureResolver
    from .resolvers.symbol_resolver import SymbolResolver

    symbol_resolver = SymbolResolver(
        (
            AbstractClassResolver(),
            CallableResolver(),
            ClassResolver(),
            PropertyResolver(),
            SignatureResolver(),
        )
    )
    return ShapeReportCollector(
        config,
        (FileResolver(), ImportResolver(), symbol_resolver),
    )


__all__ = ["standard_shape_report_collector"]
