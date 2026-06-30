from dataclasses import dataclass


@dataclass(frozen=True)
class CoherenceSummary:
    roots: tuple[str, ...]
    leaves: tuple[str, ...]
    isolated: tuple[str, ...]
    external_dependencies: tuple[str, ...]
