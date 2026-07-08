from pydantic import Field

from modwire.shared import ModwireConfig, ConfigResolver

from .boundaries.config import BoundariesConfig
from .shape.config import ShapeConfig


class ArchitectureConfig(ModwireConfig):
    language: str
    exclusions: tuple[str, ...] = ()
    boundaries: BoundariesConfig = Field(default_factory=BoundariesConfig)
    shape: ShapeConfig = Field(default_factory=ShapeConfig)


class ArchitectureConfigResolver:
    def __init__(self, config_resolver: ConfigResolver):
        self.config_resolver = config_resolver

    def resolve(self) -> ArchitectureConfig:
        return self.config_resolver.load(
            "architecture",
            ArchitectureConfig,
            "yaml",
        )
