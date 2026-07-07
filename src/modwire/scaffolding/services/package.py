from pathlib import Path

from pydantic import field_validator

from modwire.shared import ModwireBaseModel


class CodePackage(ModwireBaseModel):
    files: dict[str, str]

    @field_validator("files")
    @classmethod
    def validate_file_paths(cls, files: dict[str, str]) -> dict[str, str]:
        for path in files:
            cls._validate_file_path(path)
        return files

    @staticmethod
    def _validate_file_path(path: str) -> None:
        if not path:
            raise ValueError("Code package file path cannot be empty.")
        if "\\" in path:
            raise ValueError("Code package file path must use POSIX separators.")
        if path.startswith("/"):
            raise ValueError("Code package file path must be relative.")
        if path.endswith("/"):
            raise ValueError("Code package file path must point to a file.")

        parts = path.split("/")
        if any(part in {"", ".", ".."} for part in parts):
            raise ValueError(
                "Code package file path cannot contain empty, current, "
                "or parent segments."
            )


class CodePackageWriter:
    def write(
        self,
        package: CodePackage,
        destination: Path,
        *,
        overwrite: bool = True,
    ) -> None:
        root = destination.resolve()
        root.mkdir(parents=True, exist_ok=True)

        for path, contents in package.files.items():
            target = (root / path).resolve()
            if not target.is_relative_to(root):
                raise ValueError(
                    f"Code package file path escapes destination: {path}"
                )
            if target.exists() and not overwrite:
                raise FileExistsError(target)

            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(contents, encoding="utf-8")
