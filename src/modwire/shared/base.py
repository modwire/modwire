import abc
from pathlib import Path
from typing import Self

from pydantic import BaseModel, ConfigDict
from pydantic_yaml import parse_yaml_raw_as, to_yaml_str


class Modwire:
    supported_languages: tuple[str, ...] = ("python", "typescript", "php",)


class ModwireBaseModel(BaseModel):
    model_config = ConfigDict(frozen=True, from_attributes=True)

    def save_yaml(self, path: str | Path) -> None:
        Path(path).write_text(to_yaml_str(self), encoding="utf-8")

    @classmethod
    def load_yaml(cls, path: str | Path) -> Self:
        return parse_yaml_raw_as(cls, Path(path).read_text(encoding="utf-8"))

    def save_json(self, path: str | Path) -> None:
        Path(path).write_text(self.model_dump_json(indent=2), encoding="utf-8")

    @classmethod
    def load_json(cls, path: str | Path) -> Self:
        return cls.model_validate_json(Path(path).read_text(encoding="utf-8"))


class ModwireConfig(ModwireBaseModel):
    ...


class ModwireCLI(Modwire):
    pass


class ModwireApplication(abc.ABC, Modwire):
    @abc.abstractmethod
    def run(self):
        pass
