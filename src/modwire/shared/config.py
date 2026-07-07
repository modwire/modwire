from pathlib import Path
from typing import Literal, TypeVar

from .base import ModwireConfig

TConfig = TypeVar("TConfig", bound=ModwireConfig)


class ConfigResolver:
    def __init__(self, root: Path):
        self.root = root.resolve()
        self.dot_dir = self.root / ".modwire"

    def load(
        self,
        name: str,
        config_type: type[TConfig],
        fmt: Literal["yaml", "json"] = "yaml",
    ) -> TConfig:
        file_path = self.dot_dir / f"{name}.{fmt}"

        if fmt == "yaml":
            return config_type.load_yaml(file_path)

        return config_type.load_json(file_path)
