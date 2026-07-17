from modwire_architecture.shared import config


class ProjectsApplication:
    def __init__(
        self,
        config: config.ProjectsConfig,
    ):
        self.config = config
