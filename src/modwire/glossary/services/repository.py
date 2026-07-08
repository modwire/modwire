from wireup import injectable

from .model import Glossary


@injectable(lifetime="transient")
class GlossaryRepository:
    def __init__(self):
        self._file = "glossary.json"

    def load(self) -> Glossary:
        try:
            return Glossary.load_json(self._file)
        except FileNotFoundError:
            return Glossary()

    def save(self, glossary: Glossary) -> None:
        glossary.save_json(self._file)
