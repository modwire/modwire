import wireup

from .. import architecture, layers, modules, projects, shared
from .config import ModwireConfig


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
