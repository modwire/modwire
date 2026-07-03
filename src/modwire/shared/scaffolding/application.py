from pathlib import Path

from .copier import Scaffold
from .repository import ScaffoldRepository


class ScaffoldingApplication:
    def __init__(self, repository_root: Path) -> None:
        self.repository = ScaffoldRepository(repository_root)

    def load_scaffold(self, name: str) -> Scaffold:
        return self.repository.get_scaffold(name)

    def generate(self, name: str, destination: Path, data: dict[str, str]) -> None:
        scaffold = self.load_scaffold(name)
        scaffold.generate(destination, **data)

    def generate_from_data_items(
        self,
        name: str,
        destination: Path,
        data_items: tuple[str, ...],
    ) -> None:
        self.generate(name, destination, self.parse_data_items(data_items))

    def parse_data_items(self, items: tuple[str, ...]) -> dict[str, str]:
        return dict(self.parse_data_item(item) for item in items)

    def parse_data_item(self, item: str) -> tuple[str, str]:
        key, separator, value = item.partition("=")
        if not separator or not key:
            raise ValueError(f"Invalid data item {item!r}. Expected key=value.")
        return key, value
