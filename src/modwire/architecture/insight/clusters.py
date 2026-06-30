from pydantic import BaseModel


class ArchitectureCluster(BaseModel):
    name: str
    files: tuple[str, ...]
    incoming_count: int
    outgoing_count: int
    pressure_score: int
    top_files: tuple[str, ...]
