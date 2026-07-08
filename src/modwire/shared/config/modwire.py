from typing import Any

from pydantic import Field

from .architecture import ArchitectureConfig
from .base import ModwireBaseConfig
from .layers import LayersConfig
from .modules import ModulesConfig
from .projects import ProjectsConfig
from .scaffolding import ScaffoldingConfig


class ModwireConfig(ModwireBaseConfig):
    architecture: ArchitectureConfig | None = None
    projects: ProjectsConfig | None = None
    scaffolding: ScaffoldingConfig = Field(default_factory=ScaffoldingConfig)
    modules: ModulesConfig = Field(default_factory=ModulesConfig)
    layers: LayersConfig = Field(default_factory=LayersConfig)

    def as_wireup_config(self) -> dict[str, Any]:
        return {
            "modwire": self,
            "architecture": self.architecture,
            "projects": self.projects,
            "scaffolding": self.scaffolding,
            "modules": self.modules,
            "layers": self.layers,
        }
