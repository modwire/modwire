from .scaffold import Scaffold, ScaffoldGroup

from ..config import ScaffoldingConfig


class ScaffoldRepository:
    def __init__( self, config: ScaffoldingConfig):
        self.config = config
        self.root_dir = config.scaffolds_root

    def find_groups(self) -> list[ScaffoldGroup]:
        groups_dirs = [d for d in self.root_dir.glob("*") if d.is_dir()]
        return [ScaffoldGroup(d) for d in groups_dirs]

    def get_scaffold(self, name: str, group: str) -> Scaffold:
        scaffold_dir = self.root_dir / group / name
        return Scaffold(scaffold_dir)

    def find_all(self) -> list[Scaffold]:
        scaffolds = []
        for group in self.find_groups():
            scaffolds.extend(group.get_scaffolds())
        return scaffolds
