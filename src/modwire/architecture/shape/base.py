import abc

from pydantic import BaseModel

from .config import ShapeConfig


class ShapeViolation(BaseModel):
    source_id: str
    rule_name: str
    actual: int | str | bool
    limit: int | str | bool
    symbol_kind: str = ""
    symbol_name: str = ""


class RuleResolver(abc.ABC):
    @abc.abstractmethod
    def resolve(self, source_id: str, config: ShapeConfig) -> tuple[ShapeViolation, ...]:
        raise NotImplementedError
