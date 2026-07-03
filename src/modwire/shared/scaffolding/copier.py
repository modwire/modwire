from pathlib import Path
from tempfile import TemporaryDirectory

from copier import run_copy

from .constants import SCAFFOLD_TEMPLATES_DIRECTORY
from .package import CodePackage, CodePackageWriter


class Scaffold:
    def __init__(self, root: Path):
        assert root.is_dir(), f"Path {root} is not a directory."

        manifest_file = root / "copier.yml"
        templates_folder = root / SCAFFOLD_TEMPLATES_DIRECTORY

        assert manifest_file.is_file(
        ), f"Manifest for copier: {manifest_file} does not exist."
        assert templates_folder.is_dir(
        ), f"Templates folder for copier: {templates_folder} does not exist."

        self.root = root

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
            return self._read_package(temporary_path)

    def generate(self, destination: Path, **kwargs) -> None:
        CodePackageWriter().write(self.build_package(**kwargs), destination)

    @staticmethod
    def _read_package(root: Path) -> CodePackage:
        files = {
            path.relative_to(root).as_posix(): path.read_text(encoding="utf-8")
            for path in root.rglob("*")
            if path.is_file()
        }
        return CodePackage(files=files)
