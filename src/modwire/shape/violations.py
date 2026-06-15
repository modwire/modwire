from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ShapeViolation:
    source_id: str
    rule_name: str
    actual: int | str | bool
    limit: int | str | bool
    symbol_kind: str = ""
    symbol_name: str = ""

    def to_dict(self) -> dict[str, object]:
        return {
            "source_id": self.source_id,
            "rule_name": self.rule_name,
            "actual": self.actual,
            "limit": self.limit,
            "symbol_kind": self.symbol_kind,
            "symbol_name": self.symbol_name,
        }
