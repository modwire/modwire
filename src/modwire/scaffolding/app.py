from pathlib import Path

from wireup import injectable

from modwire.shared import code

from .services import ScaffoldRepository


@injectable(lifetime="transient")
class ScaffoldingApplication:
    def __init__(
        self, 
        repository: ScaffoldRepository,
        writer: code.CodePackageWriter,
    ):
        self.repository = repository
        self.writer = writer

    def build_package(self, scaffold_id: str, data: dict[str, str]) -> code.CodePackage:
        group, separator, name = scaffold_id.partition("/")
        if not separator or not group or not name:
            raise ValueError(f"Invalid scaffold id {scaffold_id!r}. Expected group/name.")

        scaffold = self.repository.get_scaffold(group, name)
        return scaffold.build_package(**data)

    def write_package(self, package: code.CodePackage, destination: Path):
        self.writer.write(package, destination)

    def generate(self, scaffold_id: str, destination: Path, data: dict[str, str]):
        package = self.build_package(scaffold_id, data)
        self.write_package(package, destination)
