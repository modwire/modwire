from pydantic import Field

from modwire.shared import ModwireConfig

from .boundaries import BoundariesConfig
from .shape import ShapeConfig


class ArchitectureConfig(ModwireConfig):
    language: str
    exclusions: tuple[str, ...] = ()
    boundaries: BoundariesConfig = Field(default_factory=BoundariesConfig)
    shape: ShapeConfig = Field(default_factory=ShapeConfig)
