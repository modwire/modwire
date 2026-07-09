from pathlib import Path
from typing import Any, Self

from pydantic_yaml import parse_yaml_raw_as

from ..base import ModwireBaseModel


class ModwireBaseConfig(ModwireBaseModel):
    @classmethod
    def load_yaml(cls, path: str | Path) -> Self:
        values = parse_yaml_raw_as(
            dict[str, Any],
            Path(path).read_text(encoding="utf-8"),
        )
        return cls.model_validate(
            {key: value for key, value in values.items() if value is not None}
        )
