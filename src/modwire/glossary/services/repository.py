from pathlib import Path

from .model import Glossary


class GlossaryRepository:
    def __init__(self, root: Path):
        self._file = root / "glossary.json"

    def load(self) -> Glossary:
        if self._file.exists():
            return Glossary.load_json(self._file)

        return Glossary()

    def save(self, glossary: Glossary) -> None:
        glossary.save_json(self._file)
