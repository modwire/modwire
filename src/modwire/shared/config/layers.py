from typing import Literal

from ..base import ModwireConfigModel


class Argument(ModwireConfigModel):
    name: str
    type: str


class Symbol(ModwireConfigModel):
    name: str
    role: Literal["class", "function", "variable"]
    arguments: tuple[Argument, ...] = ()


class Component(ModwireConfigModel):
    name: str
    symbols: tuple[Symbol, ...] = ()


class Layer(ModwireConfigModel):
    name: str
    layout: Literal["file", "package"]
    language: Literal["python", "php", "typescript"]
    components: tuple[Component, ...] = ()


class LayersConfig(ModwireConfigModel):
    layers: tuple[Layer, ...] = ()
