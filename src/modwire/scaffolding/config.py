from pathlib import Path

from modwire.shared import ModwireConfig


class ScaffoldingConfig(ModwireConfig):
    scaffolds_root: Path
    template_dir: str = "templates"
