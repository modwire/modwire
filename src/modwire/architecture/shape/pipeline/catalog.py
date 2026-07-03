from ..rules import (
    AbstractClassResolver,
    CallableResolver,
    ClassResolver,
    FileResolver,
    ImportResolver,
    PropertyResolver,
    SignatureResolver,
    SymbolResolver,
)

from ..base import ShapeResolver


class ShapeResolverCatalog:
    def __init__(self):
        self._resolvers = {
            resolver.name: resolver
            for resolver in (
                FileResolver(),
                ClassResolver(),
                AbstractClassResolver(),
                CallableResolver(),
                SignatureResolver(),
                PropertyResolver(),
                ImportResolver(),
                SymbolResolver(),
            )
        }

    def resolver(self, name: str) -> ShapeResolver:
        try:
            return self._resolvers[name]
        except KeyError as exc:
            known = ", ".join(sorted(self._resolvers))
            raise ValueError(
                f"Unknown shape resolver {name!r}. Known resolvers: {known}"
            ) from exc
