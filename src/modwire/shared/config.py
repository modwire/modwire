from pathlib import Path
from typing import Literal, TypeVar

from wireup import injectable

from .base import ModwireConfig
from .context import ModwireContext

TConfig = TypeVar("TConfig", bound=ModwireConfig)


@injectable
class ConfigResolver:
    def __init__(self, context: ModwireContext):
        self.context = context

    @property
    def root(self) -> Path:
        return self.context.cwd.resolve()

    @property
    def dot_dir(self) -> Path:
        return self.root / ".modwire"

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

    def resolve(
        self,
        name: str,
        config_type: type[TConfig],
        fmt: Literal["yaml", "json"] = "yaml",
        default: TConfig | None = None,
    ) -> TConfig:
        file_path = self.dot_dir / f"{name}.{fmt}"
        if default is not None and not file_path.exists():
            return default

        return self.load(name, config_type, fmt)

    def architecture(self):
        from modwire.architecture.config import ArchitectureConfig

        return self.resolve("architecture", ArchitectureConfig)

    def layers(self):
        from modwire.layers.config import LayersConfig

        return self.resolve("layers", LayersConfig)

    def modules(self):
        from modwire.modules.config import ModulesConfig

        return self.resolve("modules", ModulesConfig)

    def projects(self):
        from modwire.projects.config import ProjectsConfig

        return self.resolve("projects", ProjectsConfig)

    def scaffolding(self):
        from modwire.scaffolding.config import ScaffoldingConfig

        return self.resolve(
            "scaffolding",
            ScaffoldingConfig,
            default=ScaffoldingConfig(scaffolds_root=self.root),
        )
