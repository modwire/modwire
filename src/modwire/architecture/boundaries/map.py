from .matching import TagMap


class ArchitectureMap:
    tag_map: TagMap
    modules: dict[str, tuple[str, ...]]
    layers: dict[str, tuple[str, ...]]
    unknown_files: tuple[str, ...]

    def __init__(
        self, 
        tag_map: TagMap, 
        modules: dict[str, tuple[str, ...]], 
        layers: dict[str, tuple[str, ...]], 
        unknown_files: tuple[str, ...]
    ):
        self.tag_map = tag_map
        self.modules = modules
        self.layers = layers
        self.unknown_files = unknown_files

    