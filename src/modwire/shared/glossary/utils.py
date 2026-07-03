import re
from typing import Any


IDENTITY_FIELDS = {"id", "parent_id"}
REQUIRED_FIELDS = {*IDENTITY_FIELDS, "term", "definition"}


def slug(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-")


def deduplicate(values: list[Any]) -> list[Any]:
    deduplicated = []
    seen = set()

    for value in values:
        key = str(value)
        if key in seen:
            continue

        seen.add(key)
        deduplicated.append(value)

    return deduplicated
