from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class UnusedExport(BaseModel):
    model_config = ConfigDict(frozen=True, from_attributes=True)

    source_id: str
    name: str
    kind: str
    crossing_type: str
    reason: str


class UnusedExportInsight(ArchitectureInsight):
    model_config = ConfigDict(frozen=True, from_attributes=True)

    unused_exports: tuple[UnusedExport, ...] = ()