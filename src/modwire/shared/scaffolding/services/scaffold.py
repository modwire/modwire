import re
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

from copier import run_copy
from pydantic_yaml import parse_yaml_raw_as

from modwire.shared import code


class Scaffold:
    _name_word_pattern = re.compile(
        r"[A-Z]+(?=[A-Z][a-z0-9]|\b)|[A-Z]?[a-z0-9]+",
    )

    def __init__(self, root: Path):
        assert root.is_dir(), f"Path {root} is not a directory."

        manifest_file = root / "copier.yml"
        templates_folder = root / "templates"

        assert manifest_file.is_file(
        ), f"Manifest for copier: {manifest_file} does not exist."
        assert templates_folder.is_dir(
        ), f"Templates folder for copier: {templates_folder} does not exist."

        self.root = root

    @property
    def scaffold_id(self) -> str:
        return f"{self.root.parent.name}/{self.root.name}"

    @property
    def required_data_keys(self) -> list[str]:
        manifest = parse_yaml_raw_as(
            dict[str, Any],
            (self.root / "copier.yml").read_text(encoding="utf-8"),
        )
        return [
            key
            for key, question in manifest.items()
            if not key.startswith("_")
            and isinstance(question, dict)
            and question.get("when", True) is not False
            and "default" not in question
        ]

    def build_package(
        self,
        *,
        destination: Path | None = None,
        **kwargs,
    ) -> code.CodePackage:
        data = self._template_data(kwargs)
        with TemporaryDirectory() as temporary_directory:
            temporary_path = Path(temporary_directory)
            if destination:
                temporary_path = temporary_path / destination.name

            run_copy(
                str(self.root),
                str(temporary_path),
                data=data,
                defaults=True,
                overwrite=True,
                quiet=True,
            )

            files = {
                path.relative_to(temporary_path).as_posix(): path.read_text(encoding="utf-8")
                for path in temporary_path.rglob("*")
                if path.is_file()
            }

        return code.CodePackage(files=files)

    def _template_data(self, data: dict[str, Any]) -> dict[str, Any]:
        data = data.copy()
        if self.scaffold_id == "modules/django-api-app" and "model_name" in data:
            original_model_name = str(data["model_name"])
            model_pascal_name = self._pascal_case(original_model_name)
            data["model_name"] = model_pascal_name
            data["model_pascal_name"] = model_pascal_name
            data["model_snake_name"] = self._snake_case(original_model_name)
        return data

    def _name_words(self, value: str) -> list[str]:
        normalized = re.sub(r"[^0-9A-Za-z]+", " ", value)
        return [
            match.group(0).lower()
            for chunk in normalized.split()
            for match in self._name_word_pattern.finditer(chunk)
        ]

    def _pascal_case(self, value: str) -> str:
        return "".join(word[:1].upper() + word[1:] for word in self._name_words(value))

    def _snake_case(self, value: str) -> str:
        return "_".join(self._name_words(value))


class ScaffoldGroup:
    def __init__(self, root: Path):
        assert root.is_dir(), f"Path {root} is not a directory."
        self.root = root

    def get_scaffolds(self) -> list[Scaffold]:
        dirs = [d for d in self.root.glob("*") if d.is_dir()]
        return [Scaffold(d) for d in dirs]
