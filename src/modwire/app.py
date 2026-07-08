import wireup

import modwire.architecture
import modwire.glossary
import modwire.layers
import modwire.modules
import modwire.projects
import modwire.scaffolding
import modwire.shared

from modwire.shared import config

injectables = [
    modwire.architecture,
    modwire.glossary,
    modwire.layers,
    modwire.modules,
    modwire.projects,
    modwire.scaffolding,
    modwire.shared,
]


class ModwireApplication:
    def __init__(
        self,
        architecture: config.ArchitectureConfig | None = None,
        projects: config.ProjectsConfig | None = None,
        scaffolding: config.ScaffoldingConfig | None = None,
        modules: config.ModulesConfig | None = None,
        layers: config.LayersConfig | None = None,
    ):
        resolved_config = config.ModwireConfig()

        updates = {
            key: value
            for key, value in {
                "architecture": architecture,
                "projects": projects,
                "scaffolding": scaffolding,
                "modules": modules,
                "layers": layers,
            }.items()
            if value is not None
        }

        if updates:
            resolved_config = resolved_config.model_copy(update=updates)

        self.config = resolved_config
        self.container = wireup.create_sync_container(
            injectables=injectables,
            config=resolved_config.as_wireup_config(),
        )


application = ModwireApplication()
container = application.container
