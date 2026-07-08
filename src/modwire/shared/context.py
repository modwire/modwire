from pathlib import Path

from wireup import injectable


@injectable
class ModwireContext:
    def __init__(self):
        self.cwd = Path.cwd().resolve()
