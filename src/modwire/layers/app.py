from modwire.shared import config


class LayersApplication:
    def __init__(
        self,
        config: config.LayersConfig,
    ):
        self.config = config
