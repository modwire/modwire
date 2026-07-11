from typing import Any

from .architecture import ArchitectureApplication, ArchitectureConfig


class Modwire:
    """Small composition façade for the independently released Modwire packages."""

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
