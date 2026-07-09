from wireup import injectable

from .model import Glossary


@injectable
class GlossaryRenderer:
    def render(self, glossary: Glossary) -> str:
        return glossary.render_text()
