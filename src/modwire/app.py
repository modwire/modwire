from modwire.shared.config import ModwireConfig

from .di import create_container


class ModwireApplication:
    def __init__(self, config: ModwireConfig):
        self.config = config
        self.container = create_container(config)


def create_application(config: ModwireConfig) -> ModwireApplication:
    return ModwireApplication(config)
