from typing import Literal

from pydantic import Field

from .base import ModwireBaseConfig


class ModuleLayout(ModwireBaseConfig):
    name: str
    context_root: str
    module_root: str


class ModuleLayer(ModwireBaseConfig):
    name: str
    form: Literal["file", "package"]


class ModulesConfig(ModwireBaseConfig):
    modules: list[ModuleLayer] = Field(default_factory=list)
