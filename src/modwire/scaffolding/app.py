from pathlib import Path

from .services.scaffold import Scaffold
from .services import ScaffoldRepository, CodePackage, CodePackageWriter


class ScaffoldingApplication:
    def __init__(
        self, 
        repository: ScaffoldRepository,
        writer: CodePackageWriter,
    ):
        self.repository = repository
        self.writer = writer

    def build_package(self, scaffold_id: str, data: dict[str, str]) -> CodePackage:
        group, name = scaffold_id.split(".")
        scaffold = self.repository.get_scaffold(group, name)
        return scaffold.build_package(*data)

    def write_package(self, package: CodePackage, destination: Path):
        self.writer.write(package, destination)

    def generate(self, scaffold_id: str, destination: Path, data: dict[str, str]):
        package = self.build_package(scaffold_id, data)
        self.write_package(package, destination)
