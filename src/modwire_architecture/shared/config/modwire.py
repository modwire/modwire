from pydantic import Field

from .architecture import ArchitectureConfig
from ..base import ModwireConfigModel
from .layers import LayersConfig
from .modules import ModulesConfig
from .projects import ProjectsConfig


class ModwireConfig(ModwireConfigModel):
    architecture: ArchitectureConfig = Field(default_factory=ArchitectureConfig)
    projects: ProjectsConfig = Field(default_factory=ProjectsConfig)
    modules: ModulesConfig = Field(default_factory=ModulesConfig)
    layers: LayersConfig = Field(default_factory=LayersConfig)
