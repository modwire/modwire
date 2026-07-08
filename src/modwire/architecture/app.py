from modwire.shared import ModwireApplication

from .config import ArchitectureConfigResolver
from .map import ArchitectureMapLoader


class ArchitectureApplication(ModwireApplication):
    config_resolver: ArchitectureConfigResolver
    map_loader: ArchitectureMapLoader

    def run(self):
        pass
