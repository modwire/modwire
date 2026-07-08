from pathlib import Path

from modwire.shared import ModwireConfig, ConfigResolver


class ScaffoldingConfig(ModwireConfig):
    scaffolds_root: Path
    template_dir: str = "templates"


class ScaffoldingConfigResolver:
    def __init__(self, config_resolver: ConfigResolver):
        self.config_resolver = config_resolver

    def resolve(self) -> ScaffoldingConfig:
        config_path = self.config_resolver.dot_dir / "scaffolding.yaml"
        if not config_path.exists():
            return ScaffoldingConfig(scaffolds_root=self.config_resolver.root)

        return self.config_resolver.load(
            "scaffolding",
            ScaffoldingConfig,
            "yaml",
        )
