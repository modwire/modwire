from wireup import injectable

from .model import Glossary


@injectable
class GlossaryRenderer:
    def render(self, glossary: Glossary) -> None:
        text = glossary.render_text()
        if text:
            print(text)
