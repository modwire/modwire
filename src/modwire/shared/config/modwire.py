from pathlib import Path
from typing import Any, Self

from pydantic import Field

from .architecture import ArchitectureConfig, BoundariesConfig
from .base import ModwireBaseConfig
from .layers import LayersConfig
from .modules import ModulesConfig
from .projects import ProjectsConfig
from .shape import ShapeConfig


class ModwireConfig(ModwireBaseConfig):
    architecture: ArchitectureConfig = Field(default_factory=ArchitectureConfig)
    projects: ProjectsConfig = Field(default_factory=ProjectsConfig)
    modules: ModulesConfig = Field(default_factory=ModulesConfig)
    layers: LayersConfig = Field(default_factory=LayersConfig)

    def as_wireup_config(self) -> dict[str, Any]:
        values = {
            "modwire": self,
            "architecture": self.architecture,
            "projects": self.projects,
            "modules": self.modules,
            "layers": self.layers,
        }
        return {key: value for key, value in values.items()}

    @classmethod
    def load_dir(cls, root: Path) -> Self:
        if not root.is_dir():
            raise ValueError(f"Config directory does not exist: {root}")

        loaders = {
            "architecture": (("architecture",), ArchitectureConfig),
            "projects": (("projects",), ProjectsConfig),
            "modules": (("modules",), ModulesConfig),
            "layers": (("layers",), LayersConfig),
            "boundaries": (("architecture", "boundaries"), BoundariesConfig),
            "shape": (("architecture", "shape"), ShapeConfig),
        }

        kwargs: dict[str, Any] = {}
        yamls = sorted((*root.glob("*.yaml"), *root.glob("*.yml")))
        for yaml in yamls:
            loader = loaders.get(yaml.stem)
            if loader is None:
                raise ValueError(f"Unknown Modwire config file: {yaml.name}")

            keys, config_cls = loader
            config = config_cls.load_yaml(yaml).model_dump()

            if len(keys) == 1 and isinstance(kwargs.get(keys[0]), dict):
                kwargs[keys[0]] = {**config, **kwargs[keys[0]]}
                continue

            target = kwargs
            for key in keys[:-1]:
                target = target.setdefault(key, {})
            target[keys[-1]] = config

        return cls(**kwargs)
