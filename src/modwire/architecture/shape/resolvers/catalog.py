from wireup import injectable

from ..base import ShapeResolverInterface
from .abstract_class_resolver import AbstractClassResolver
from .callable_resolver import CallableResolver
from .class_resolver import ClassResolver
from .file_resolver import FileResolver
from .import_resolver import ImportResolver
from .property_resolver import PropertyResolver
from .signature_resolver import SignatureResolver
from .symbol_resolver import SymbolResolver


class ShapeResolverCatalog:
    def __init__(
        self,
        resolvers: list[ShapeResolverInterface],
    ):
        self._resolvers = {resolver.name: resolver for resolver in resolvers}

    def resolver(self, name: str) -> ShapeResolverInterface:
        try:
            return self._resolvers[name]
        except KeyError as error:
            known = ", ".join(sorted(self._resolvers))
            raise ValueError(
                f"Unknown shape resolver {name!r}. Known resolvers: {known}"
            ) from error

    def names(self) -> tuple[str, ...]:
        return tuple(self._resolvers)


@injectable
def create_shape_resolver_catalog() -> ShapeResolverCatalog:
    return ShapeResolverCatalog(
        resolvers=[
            FileResolver(),
            ClassResolver(),
            AbstractClassResolver(),
            CallableResolver(),
            SignatureResolver(),
            PropertyResolver(),
            ImportResolver(),
            SymbolResolver(),
        ],
    )
