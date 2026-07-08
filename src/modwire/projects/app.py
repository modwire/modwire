from modwire.shared import ModwireApplication

from .config import ProjectsConfig


class ProjectsApplication(ModwireApplication):
    def __init__(self, config: ProjectsConfig):
        self.config = config

    def run(self):
        print("Running Modwire Projects...")

    def init(self, name: str, language: str, package_manager: str):
        pass

    def add_dependencies(self, names: list[str], group: str = ""):
        pass

    def remove_dependencies(self, names: list[str], group: str = ""):
        pass

    def add_module(self, name: str):
        pass

    def add_layer(self, name: str, module: str):
        pass

    def add_package(self, name: str, module: str, layer: str):
        pass
