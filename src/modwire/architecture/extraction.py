from pathlib import Path

from modwire_extraction import ModwireExtraction
from modwire_extraction.code import QueryableCodeMap


def extract_code_map(root_path: Path, language: str) -> QueryableCodeMap:
    return ModwireExtraction(root_path).generate_queryable_map(language)