from pydantic import (BaseModel, ConfigDict, Field, )

from .boundaries.config import BoundariesConfig
from .shape.config import ShapeConfig


class ArchitectureConfig(BaseModel):
    model_config = ConfigDict(frozen=True, from_attributes=True)

    language: str
    exclusions: tuple[str, ...] = ()
    boundaries: BoundariesConfig = Field(default_factory=BoundariesConfig)
    shape: ShapeConfig = Field(default_factory=ShapeConfig)
    root: str = ""
