import json
from pathlib import Path


def read_glossary(cwd: Path) -> dict:
    return json.loads((cwd / "glossary.json").read_text(encoding="utf-8"))
