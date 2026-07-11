from modwire.shared import config


class ModulesApplication:
    def __init__(
        self,
        config: config.ModulesConfig,
    ):
        self.config = config
