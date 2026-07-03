from typing import Literal

from modwire.shared import ModwireConfig


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
