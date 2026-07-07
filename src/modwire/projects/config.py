from typing import Literal

from pydantic import Field

from modwire.shared import ModwireConfig, ConfigResolver


class ProjectLayout(ModwireConfig):
    package_root: str
    template: Literal["CONTEXT.MODULE.LAYER", "MODULE.LAYER"]
    module_template: Literal["HEXAGONAL", "LAYERED"]


class ProjectStack(ModwireConfig):
    language: str
    language_version: str
    package_manager: str
    framework: str
    dependencies: tuple[str, ...] = ()
    dev_dependencies: tuple[str, ...] = ()
    scripts: dict[str, str] = Field(default_factory=dict)


class ProjectsConfig(ModwireConfig):
    name: str
    stack: ProjectStack
    layout: ProjectLayout


class ProjectsConfigResolver:
    def __init__(self, config_resolver: ConfigResolver):
        self.config_resolver = config_resolver

    def resolve(self) -> ProjectsConfig:
        return self.config_resolver.load(
            "projects",
            ProjectsConfig,
            "yaml",
        )
