from modwire.shared import ModwireBaseModel

from ..map import ArchitectureMap


class ArchitectureGroup(ModwireBaseModel):
    name: str
    source_ids: tuple[str, ...]


class ArchitectureMapReport(ModwireBaseModel):
    modules: tuple[ArchitectureGroup, ...] = ()
    layers: tuple[ArchitectureGroup, ...] = ()
    unknown_files: tuple[str, ...] = ()

    @classmethod
    def from_map(cls, architecture_map: ArchitectureMap) -> "ArchitectureMapReport":
        return cls(
            modules=tuple(
                ArchitectureGroup(name=name, source_ids=source_ids)
                for name, source_ids in sorted(architecture_map.modules.items())
            ),
            layers=tuple(
                ArchitectureGroup(name=name, source_ids=source_ids)
                for name, source_ids in sorted(architecture_map.layers.items())
            ),
            unknown_files=architecture_map.unknown_files,
        )
