from pydantic import BaseModel


class CoherenceSummary(BaseModel):
    roots: tuple[str, ...]
    leaves: tuple[str, ...]
    isolated: tuple[str, ...]
    external_dependencies: tuple[str, ...]
