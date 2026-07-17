from types import SimpleNamespace

import pytest

from modwire_architecture.architecture.shape.resolvers.import_resolver import ImportResolver
from modwire_architecture.shared.config import ShapeConfig


class ImportQuery:
    def __init__(self, *imports):
        self._imports = imports

    def imports(self):
        return self

    def all(self):
        return self._imports


def import_result(crossing_type: str, *, uses_joined_import: bool):
    source_import = SimpleNamespace(
        crossing_type=crossing_type,
        uses_joined_import=uses_joined_import,
        is_aliased=False,
        normalized_path="package.api",
        join_key="package.api",
    )
    return SimpleNamespace(source_id="consumer.py", item=source_import)


@pytest.mark.parametrize(
    ("crossing_type", "uses_joined_import"),
    (("module", False), ("symbol", True)),
)
def test_default_import_shape_allows_module_and_joined_symbol_imports(
    crossing_type: str,
    uses_joined_import: bool,
) -> None:
    architecture_map = SimpleNamespace(
        code_map=ImportQuery(
            import_result(crossing_type, uses_joined_import=uses_joined_import)
        )
    )

    assert ImportResolver().resolve(architecture_map, ShapeConfig()) == ()


def test_default_import_shape_rejects_unjoined_symbol_imports() -> None:
    architecture_map = SimpleNamespace(
        code_map=ImportQuery(import_result("symbol", uses_joined_import=False))
    )

    violations = ImportResolver().resolve(architecture_map, ShapeConfig())

    assert tuple(violation.rule_name for violation in violations) == (
        "require_joined_imports",
    )
