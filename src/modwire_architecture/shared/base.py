import abc
import json
from typing import Any, Self

from pydantic import BaseModel, ConfigDict
from pydantic_yaml import parse_yaml_raw_as, to_yaml_str

class ModwireModel(BaseModel):
    """Strict public value model used across the Modwire ecosystem."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        arbitrary_types_allowed=True,
        validate_default=True,
    )

    def to_json(self, *, indent: int | None = 2) -> str:
        return self.model_dump_json(indent=indent)

    @classmethod
    def from_json(cls, value: str | bytes | bytearray) -> Self:
        return cls.model_validate_json(value)

    def to_yaml(self) -> str:
        return to_yaml_str(self)

    @classmethod
    def from_yaml(cls, value: str) -> Self:
        return parse_yaml_raw_as(cls, value)

    def to_dict(self, **kwargs: Any) -> dict[str, Any]:
        return self.model_dump(**kwargs)

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> Self:
        return cls.model_validate(value)

    def pretty(self) -> str:
        return json.dumps(self.model_dump(mode="json"), indent=2, sort_keys=True)


class ModwireConfigModel(ModwireModel):
    """Base class for declarative Modwire configuration."""

    @classmethod
    def from_yaml(cls, value: str) -> Self:
        values = parse_yaml_raw_as(dict[str, Any], value)
        return cls.model_validate(
            {key: item for key, item in values.items() if item is not None}
        )


class ModwireReportModel(ModwireModel):
    """Base class for serializable Modwire report contracts."""


class ModwireBaseApplication(abc.ABC):
    @abc.abstractmethod
    def run(self):
        pass
