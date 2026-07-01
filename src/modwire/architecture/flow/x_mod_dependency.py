from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class CrossModuleDependency(BaseModel):
    model_config = ConfigDict(frozen=True, from_attributes=True)

    source: str
    target: str
    count: int


__all__ = ["CrossModuleDependency"]
