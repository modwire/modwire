from .architecture import ArchitectureApplication, ArchitectureConfig


class Modwire:
    """Small façade for Architecture reporting."""

    def architecture(
        self,
        config: ArchitectureConfig,
    ) -> ArchitectureApplication:
        return ArchitectureApplication.standard(config)
