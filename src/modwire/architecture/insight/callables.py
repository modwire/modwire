from pydantic import BaseModel


class CallableReportEntry(BaseModel):
    source_callable: str
    calls: tuple[str, ...]
    callers: tuple[str, ...]
