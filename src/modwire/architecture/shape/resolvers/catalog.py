from ..base import ShapeResolverInterface


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
