from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

from copier import run_copy
from pydantic_yaml import parse_yaml_raw_as

from modwire.shared import code


class Scaffold:
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
        with TemporaryDirectory() as temporary_directory:
            temporary_path = Path(temporary_directory)
            if destination:
                temporary_path = temporary_path / destination.name

            run_copy(
                str(self.root),
                str(temporary_path),
                data=kwargs,
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


class ScaffoldGroup:
    def __init__(self, root: Path):
        assert root.is_dir(), f"Path {root} is not a directory."
        self.root = root

    def get_scaffolds(self) -> list[Scaffold]:
        dirs = [d for d in self.root.glob("*") if d.is_dir()]
        return [Scaffold(d) for d in dirs]
