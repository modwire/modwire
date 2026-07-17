from modwire_extraction.code import QueryableCodeMap
from modwire_architecture.shared import ModwireModel


class ArchitectureRealm(ModwireModel):
    name: str
    module_tag: str
    layers: tuple[str, ...] = ()


class ArchitectureMap(ModwireModel):
    code_map: QueryableCodeMap
    tag_map: object
    modules: dict[str, tuple[str, ...]]
    layers: dict[str, tuple[str, ...]]
    unknown_files: tuple[str, ...]
    realm: ArchitectureRealm

    def with_realm(self, realm: ArchitectureRealm) -> "ArchitectureMap":
        return self.model_copy(update={"realm": realm})
