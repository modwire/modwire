from typing import Literal

from pydantic import Field

from .base import ModwireBaseConfig


class ProjectLayout(ModwireBaseConfig):
    package_root: str
    template: Literal["CONTEXT.MODULE.LAYER", "MODULE.LAYER"]
    module_template: Literal["HEXAGONAL", "LAYERED"]


class ProjectStack(ModwireBaseConfig):
    language: str
    language_version: str
    package_manager: str
    framework: str
    dependencies: tuple[str, ...] = ()
    dev_dependencies: tuple[str, ...] = ()
    scripts: dict[str, str] = Field(default_factory=dict)


class ProjectsConfig(ModwireBaseConfig):
    name: str
    stack: ProjectStack
    layout: ProjectLayout
