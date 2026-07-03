from typing import Literal

from modwire.shared import ModwireConfig


class ModuleLayout(ModwireConfig):
    name: str
    context_root: str
    module_root: str


class ModuleLayer(ModwireConfig):
    name: str
    form: Literal["file", "package"]
