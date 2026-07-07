from typing import Literal

from modwire.shared import ModwireConfig, ConfigResolver


class ModuleLayout(ModwireConfig):
    name: str
    context_root: str
    module_root: str


class ModuleLayer(ModwireConfig):
    name: str
    form: Literal["file", "package"]


class ModulesConfig(ModwireConfig):
    modules: list[ModuleLayer]


class ModulesConfigResolver:
    def __init__(self, config_resolver: ConfigResolver):
        self.config_resolver = config_resolver

    def resolve(self) -> ModulesConfig:
        return self.config_resolver.load(
            "modules",
            ModulesConfig,
            "yaml",
        )
