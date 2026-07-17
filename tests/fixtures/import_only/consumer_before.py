from modwire import ArchitectureConfig, Modwire


def catalog():
    return Modwire().architecture(ArchitectureConfig()).reports()
