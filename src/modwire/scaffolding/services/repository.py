from pathlib import Path

from .scaffold import Scaffold, ScaffoldGroup

from ..config import ScaffoldingConfig


class ScaffoldRepository:
    def __init__(self, config: ScaffoldingConfig):
        self.config = config
        self.root_dirs = (
            config.scaffolds_root,
            Path(__file__).resolve().parents[3] / "scaffoldings",
        )

    def find_groups(self) -> list[ScaffoldGroup]:
        groups = []
        seen = set()

        for root_dir in self.root_dirs:
            for group_dir in root_dir.glob("*"):
                if not group_dir.is_dir() or group_dir.name in seen:
                    continue

                seen.add(group_dir.name)
                groups.append(ScaffoldGroup(group_dir))

        return groups

    def get_scaffold(self, group: str, name: str) -> Scaffold:
        for root_dir in self.root_dirs:
            scaffold_dir = root_dir / group / name
            if scaffold_dir.is_dir():
                return Scaffold(scaffold_dir)

        known = ", ".join(scaffold.scaffold_id for scaffold in self.find_all())
        raise ValueError(
            f"Unknown scaffold {f'{group}/{name}'!r}. Known scaffolds: {known}"
        )

    def find_all(self) -> list[Scaffold]:
        scaffolds = []
        for group in self.find_groups():
            scaffolds.extend(group.get_scaffolds())
        return scaffolds
