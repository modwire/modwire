from pathlib import Path

from .constants import BUNDLED_SCAFFOLDS_ROOT, SCAFFOLD_TEMPLATES_DIRECTORY
from .copier import Scaffold


class ScaffoldRepository:
    def __init__(
        self,
        root: Path,
        bundled_root: Path = BUNDLED_SCAFFOLDS_ROOT,
    ):
        assert root.is_dir(), f"Path {root} is not a directory."
        self.root = root
        self.bundled_root = bundled_root

    def get_scaffold(self, name: str) -> Scaffold:
        scaffold_path = self.resolve_scaffold_path(name)
        return Scaffold(scaffold_path)

    def resolve_scaffold_path(self, name: str) -> Path:
        requested_path = Path(name)
        candidates = []

        if requested_path.is_absolute():
            candidates.append(requested_path)
        else:
            candidates.append(self.root / requested_path)
            candidates.append(self.bundled_root / requested_path)

        for candidate in candidates:
            if candidate.is_dir():
                return candidate

        known = ", ".join(self.list_bundled_scaffolds())
        raise ValueError(
            f"Unknown scaffold {name!r}. Known bundled scaffolds: {known}"
        )

    def list_bundled_scaffolds(self) -> tuple[str, ...]:
        return tuple(
            path.relative_to(self.bundled_root).as_posix()
            for path in sorted(self.bundled_root.rglob("copier.yml"))
            if (path.parent / SCAFFOLD_TEMPLATES_DIRECTORY).is_dir()
        )
