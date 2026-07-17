from typing import Literal

from ..base import ModwireConfigModel


class ModuleLayout(ModwireConfigModel):
    name: str
    context_root: str
    module_root: str


class ModuleLayer(ModwireConfigModel):
    name: str
    form: Literal["file", "package"]


class ModulesConfig(ModwireConfigModel):
    modules: tuple[ModuleLayer, ...] = ()
