from pathlib import Path
from typing import Any

from modwire_extraction.code import QueryableCodeMap

from .architecture import ArchitectureApplication, ArchitectureConfig
from .code import QueryableCodeMapReader


class Modwire:
    """Small composition façade for the independently released Modwire packages."""

    def extract(self, root: str | Path, language: str) -> QueryableCodeMap:
        return QueryableCodeMapReader().read(Path(root), language)

    def architecture(
        self,
        config: ArchitectureConfig | None = None,
    ) -> ArchitectureApplication:
        return ArchitectureApplication.standard(config)

    def mermaid(self) -> Any:
        from modwire_mermaid import ModwireMermaidFactory

        return ModwireMermaidFactory.standard()

    def siren(self, schema: dict[str, Any], base_url: str) -> Any:
        from modwire_siren import ModwireSirenFactory

        return ModwireSirenFactory.standard(schema, base_url)
