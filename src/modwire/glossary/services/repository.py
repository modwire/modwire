from wireup import injectable

from modwire.shared import ModwireContext

from .model import Glossary


@injectable(lifetime="transient")
class GlossaryRepository:
    def __init__(self, context: ModwireContext):
        self._file = context.cwd / "glossary.json"

    def load(self) -> Glossary:
        if self._file.exists():
            return Glossary.load_json(self._file)

        return Glossary()

    def save(self, glossary: Glossary) -> None:
        glossary.save_json(self._file)
