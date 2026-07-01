from pydantic import BaseModel


class DependencyHotspot(BaseModel):
    source_id: str
    incoming_count: int
    outgoing_count: int
    pressure_score: int
