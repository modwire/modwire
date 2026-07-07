from modwire.shared import ModwireApplication

from .config import ArchitectureConfig


class ArchitectureApplication(ModwireApplication):
    def __init__(self, config: ArchitectureConfig):
        self.config = config

    def run(self):
        pass
