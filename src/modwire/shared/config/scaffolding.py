from pathlib import Path

from .base import ModwireBaseConfig


class ScaffoldingConfig(ModwireBaseConfig):
    scaffolds_root: Path
    template_dir: str = "templates"
