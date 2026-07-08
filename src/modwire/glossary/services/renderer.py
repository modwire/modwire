from .model import Glossary


class GlossaryRenderer:
    def render(self, glossary: Glossary) -> None:
        text = glossary.render_text()
        if text:
            print(text)
