from dataclasses import dataclass


@dataclass(frozen=True)
class DependencyHotspot:
    source_id: str
    incoming_count: int
    outgoing_count: int
    pressure_score: int
