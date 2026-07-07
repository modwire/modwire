from pathlib import Path

from modwire.shared import ModwireConfig, ConfigResolver


class ScaffoldingConfig(ModwireConfig):
    scaffolds_root: Path
    template_dir: str = "templates"


class ScaffoldingConfigResolver:
    def __init__(self, config_resolver: ConfigResolver):
        self.config_resolver = config_resolver

    def resolve(self) -> ScaffoldingConfig:
        return self.config_resolver.load(
            "scaffolding",
            ScaffoldingConfig,
            "yaml",
        )
