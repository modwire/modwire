from pydantic import Field

from modwire.shared import ModwireConfig

from .boundaries.config import BoundariesConfig
from .shape.config import ShapeConfig


class ArchitectureConfig(ModwireConfig):
    language: str
    exclusions: tuple[str, ...] = ()
    boundaries: BoundariesConfig = Field(default_factory=BoundariesConfig)
    shape: ShapeConfig = Field(default_factory=ShapeConfig)
