from typing import Literal

from pydantic import Field

from modwire.shared import ModwireConfig


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


class ProjectConfig(ModwireConfig):
    name: str
    stack: ProjectStack
    layout: ProjectLayout
