from dependency_injector import containers, providers

from ..base import ShapeResolverInterface
from .abstract_class_resolver import AbstractClassResolver
from .callable_resolver import CallableResolver
from .catalog import ShapeResolverCatalog
from .class_resolver import ClassResolver
from .file_resolver import FileResolver
from .import_resolver import ImportResolver
from .property_resolver import PropertyResolver
from .signature_resolver import SignatureResolver
from .symbol_resolver import SymbolResolver


def _default_shape_resolvers() -> list[ShapeResolverInterface]:
    return [
        FileResolver(),
        ClassResolver(),
        AbstractClassResolver(),
        CallableResolver(),
        SignatureResolver(),
        PropertyResolver(),
        ImportResolver(),
        SymbolResolver(),
    ]


class ShapeResolversContainer(containers.DeclarativeContainer):
    catalog = providers.Singleton(
        ShapeResolverCatalog,
        resolvers=providers.Callable(_default_shape_resolvers),
    )
