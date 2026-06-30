from dataclasses import dataclass


@dataclass(frozen=True)
class ArchitectureCluster:
    name: str
    files: tuple[str, ...]
    incoming_count: int
    outgoing_count: int
    pressure_score: int
    top_files: tuple[str, ...]
