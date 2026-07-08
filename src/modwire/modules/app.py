from typing import Annotated

from wireup import Inject, injectable

from modwire.shared import config


@injectable(lifetime="transient")
class ModulesApplication:
    def __init__(
        self,
        config: Annotated[config.ModulesConfig, Inject(config="modules")],
    ):
        self.config = config

    def scaffold(self, name: str, target: str):
        pass

    def add_layer(self, name: str):
        pass

    def remove_layer(self, name: str):
        pass

    def add_package(self, name: str, layer: str):
        pass

    def remove_package(self, name: str, layer: str):
        pass
