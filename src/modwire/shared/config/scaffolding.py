from pathlib import Path

from .base import ModwireBaseConfig


class ScaffoldingConfig(ModwireBaseConfig):
    scaffolds_root: Path = Path(".modwire/scaffoldings")
    template_dir: str = "templates"
