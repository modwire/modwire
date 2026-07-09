import wireup

from modwire import (
    architecture,
    layers,
    modules,
    projects,
    shared,
)

from modwire.shared import config


def create_container(modwire_config: config.ModwireConfig):
    injectables = [
        architecture,
        layers,
        modules,
        projects,
        shared,
    ]

    return wireup.create_sync_container(
        injectables=injectables,
        config=modwire_config.as_wireup_config(),
    )


def create_application(
    *,
    architecture: config.ArchitectureConfig | None = None,
    projects: config.ProjectsConfig | None = None,
    scaffolding: config.ScaffoldingConfig | None = None,
    modules: config.ModulesConfig | None = None,
    layers: config.LayersConfig | None = None,
) -> "ModwireApplication":
    return ModwireApplication(
        architecture=architecture,
        projects=projects,
        scaffolding=scaffolding,
        modules=modules,
        layers=layers,
    )


class ModwireApplication:
    def __init__(
        self,
        architecture: config.ArchitectureConfig,
        projects: config.ProjectsConfig,
        scaffolding: config.ScaffoldingConfig,
        modules: config.ModulesConfig,
        layers: config.LayersConfig,
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
        self.container = create_container(resolved_config)


application = create_application()
container = application.container
