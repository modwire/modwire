import abc
from pathlib import Path
from typing import Self, TypeVar, Literal

from pydantic import BaseModel, ConfigDict
from pydantic_yaml import parse_yaml_raw_as, to_yaml_str


TConfig = TypeVar("TConfig", bound="ModwireConfig")


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
    def __init__(self, cwd: Path):
        self.cwd = cwd.resolve()
        self.dot_dir = self.cwd / ".modwire"
    
    def load_config(self, name: str, config_type: type[TConfig], fmt: Literal["yaml", "json"]) -> TConfig:
        file_path = self.dot_dir / f"{name}.{fmt}"
        if fmt == "yaml":
            return config_type.load_yaml(file_path)
        return config_type.load_json(file_path)


class ModwireApplication(abc.ABC, Modwire):
    @abc.abstractmethod
    def run(self):
        pass
