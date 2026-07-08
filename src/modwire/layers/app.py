from typing import Annotated

from wireup import injectable, Inject

from modwire.shared import config


@injectable(lifetime="transient")
class LayersApplication:
    def __init__(
        self,
        config: Annotated[config.LayersConfig, Inject(config="layers")],
    ):
        self.config = config

    def scaffold(self, name: str, layout: str, language: str):
        pass

    def add_layer(self, name: str):
        pass

    def remove_layer(self, name: str):
        pass

    def add_package(self, name: str, layer: str):
        pass

    def remove_package(self, name: str, layer: str):
        pass
