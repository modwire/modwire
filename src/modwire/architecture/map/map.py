from modwire_extraction.code import QueryableCodeMap

from ..config import ArchitectureConfig
from ..boundaries.config import FlowRealm
from ..boundaries.tags import TagMap


class ArchitectureMap:
    config: ArchitectureConfig
    realm: FlowRealm
    code_map: QueryableCodeMap
    tag_map: TagMap
    modules: dict[str, tuple[str, ...]]
    layers: dict[str, tuple[str, ...]]
    unknown_files: tuple[str, ...]

    def __init__(
        self,
        config: ArchitectureConfig,
        code_map: QueryableCodeMap,
        tag_map: TagMap,
        modules: dict[str, tuple[str, ...]],
        layers: dict[str, tuple[str, ...]],
        unknown_files: tuple[str, ...],
        realm: FlowRealm | None = None,
    ):
        self.config = config
        self.realm = realm or FlowRealm(
            module_tag=config.boundaries.flow.module_tag,
            layers=config.boundaries.flow.layers,
        )
        self.code_map = code_map
        self.tag_map = tag_map
        self.modules = modules
        self.layers = layers
        self.unknown_files = unknown_files

    def with_realm(self, realm: FlowRealm) -> "ArchitectureMap":
        return ArchitectureMap(
            config=self.config,
            code_map=self.code_map,
            tag_map=self.tag_map,
            modules=self.modules,
            layers=self.layers,
            unknown_files=self.unknown_files,
            realm=realm,
        )



