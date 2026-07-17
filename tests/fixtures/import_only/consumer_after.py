from modwire_architecture import ArchitectureConfig, Modwire


def catalog():
    return Modwire().architecture(ArchitectureConfig()).reports()
