import wireup

from modwire import architecture, layers, modules, projects, shared
from modwire.shared.config import ModwireConfig


def create_container(config: ModwireConfig):
    return wireup.create_sync_container(
        injectables=[
            architecture,
            layers,
            modules,
            projects,
            shared.code,
            shared.glossary,
            shared.scaffolding,
        ],
        config=config.as_wireup_config(),
    )
