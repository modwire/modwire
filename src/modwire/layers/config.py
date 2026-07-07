from typing import Literal

from modwire.shared import ModwireConfig, ConfigResolver


class Argument(ModwireConfig):
    name: str
    type: str


class Symbol(ModwireConfig):
    name: str
    role: Literal["class", "function", "variable"]
    arguments: tuple[Argument, ...] = ()


class Component(ModwireConfig):
    name: str
    symbols: tuple[Symbol, ...] = ()


class Layer(ModwireConfig):
    name: str
    layout: Literal["file", "package"]
    language: Literal["python", "php", "typescript"]
    components: tuple[Component, ...] = ()


class LayersConfig(ModwireConfig):
    layers: list[Layer]


class LayersConfigResolver:
    def __init__(self, config_resolver: ConfigResolver):
        self.config_resolver = config_resolver

    def resolve(self) -> LayersConfig:
        return self.config_resolver.load(
            "layers",
            LayersConfig,
            "yaml",
        )
