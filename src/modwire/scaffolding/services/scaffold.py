from pathlib import Path
from tempfile import TemporaryDirectory

from copier import run_copy

from .package import CodePackage


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

    def build_package(self, **kwargs) -> CodePackage:
        with TemporaryDirectory() as temporary_directory:
            temporary_path = Path(temporary_directory)
            
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

        return CodePackage(files=files)


class ScaffoldGroup:
    def __init__(self, root: Path):
        assert root.is_dir(), f"Path {root} is not a directory."
        self.root = root

    def get_scaffolds(self) -> list[Scaffold]:
        dirs = [d for d in self.root.glob("*") if d.is_dir()]
        return [Scaffold(d) for d in dirs]
