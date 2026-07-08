from typing import Self

from modwire_extraction.code import QueryableCodeMap

from modwire.shared import config


class ArchitectureMap:
    realm: config.FlowRealm
    code_map: QueryableCodeMap
    tag_map: TagMap
    modules: dict[str, tuple[str, ...]]
    layers: dict[str, tuple[str, ...]]
    unknown_files: tuple[str, ...]

    def __init__(
        self,
        config: config.ArchitectureConfig,
        code_map: QueryableCodeMap,
        tag_map: TagMap,
        modules: dict[str, tuple[str, ...]],
        layers: dict[str, tuple[str, ...]],
        unknown_files: tuple[str, ...],
        realm: config.FlowRealm | None = None,
    ):
        self.config = config
        self.realm = realm or config.FlowRealm(
            module_tag=config.boundaries.flow.module_tag,
            layers=config.boundaries.flow.layers,
        )
        self.code_map = code_map
        self.tag_map = tag_map
        self.modules = modules
        self.layers = layers
        self.unknown_files = unknown_files


