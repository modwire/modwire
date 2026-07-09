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
            shared,
        ],
        config=config.as_wireup_config(),
    )
