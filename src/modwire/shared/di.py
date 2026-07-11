import wireup

from .. import architecture, code, layers, modules, projects
from .config import ModwireConfig


def create_container(config: ModwireConfig):
    return wireup.create_sync_container(
        injectables=[
            architecture,
            code,
            layers,
            modules,
            projects,
        ],
        config=config.as_wireup_config(),
    )
