from dataclasses import dataclass

from modwire_extraction.code import QueryableCodeMap

from ..boundaries.tags import TagMap


@dataclass(frozen=True)
class ArchitectureRealm:
    name: str
    module_tag: str
    layers: tuple[str, ...] = ()


class ArchitectureMap:
    def __init__(
        self,
        code_map: QueryableCodeMap,
        tag_map: TagMap,
        modules: dict[str, tuple[str, ...]],
        layers: dict[str, tuple[str, ...]],
        unknown_files: tuple[str, ...],
        realm: ArchitectureRealm,
    ):
        self.realm = realm
        self.code_map = code_map
        self.tag_map = tag_map
        self.modules = modules
        self.layers = layers
        self.unknown_files = unknown_files

    def with_realm(self, realm: ArchitectureRealm) -> "ArchitectureMap":
        return ArchitectureMap(
            code_map=self.code_map,
            tag_map=self.tag_map,
            modules=self.modules,
            layers=self.layers,
            unknown_files=self.unknown_files,
            realm=realm,
        )
