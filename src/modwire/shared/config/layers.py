from typing import Literal

from .base import ModwireBaseConfig


class Argument(ModwireBaseConfig):
    name: str
    type: str


class Symbol(ModwireBaseConfig):
    name: str
    role: Literal["class", "function", "variable"]
    arguments: tuple[Argument, ...] = ()


class Component(ModwireBaseConfig):
    name: str
    symbols: tuple[Symbol, ...] = ()


class Layer(ModwireBaseConfig):
    name: str
    layout: Literal["file", "package"]
    language: Literal["python", "php", "typescript"]
    components: tuple[Component, ...] = ()


class LayersConfig(ModwireBaseConfig):
    layers: list[Layer]
