from typing import Literal, TypeVar

from wireup import injectable

from .base import ModwireConfig

TConfig = TypeVar("TConfig", bound=ModwireConfig)


@injectable
class ConfigResolver:    
    def load(
        self,
        name: str,
        config_type: type[TConfig],
        fmt: Literal["yaml", "json"] = "yaml",
    ) -> TConfig:

        if fmt == "yaml":
            return config_type.load_yaml(file_path)

        return config_type.load_json(file_path)

    def resolve(
        self,
        name: str,
        config_type: type[TConfig],
        fmt: Literal["yaml", "json"] = "yaml",
    ) -> TConfig:
        file_path = self.dot_dir / f"{name}.{fmt}"
        if default is not None and not file_path.exists():
            return default

        return self.load(name, config_type, fmt)