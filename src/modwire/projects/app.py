from typing import Annotated

from wireup import injectable, Inject

from modwire.shared import config


@injectable(lifetime="transient")
class ProjectsApplication:
    def __init__(
        self,
        config: Annotated[config.ProjectsConfig, Inject(config="projects")],
    ):
        self.config = config

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
