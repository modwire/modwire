import ast
import json
from pathlib import Path

import pytest

from modwire.projects import generate_project, get_project_profile


def test_generate_project_uses_caller_copier_template(tmp_path: Path) -> None:
    template_root = tmp_path / "template-root"
    template_dir = template_root / "template"
    template_dir.mkdir(parents=True)
    (template_root / "copier.yml").write_text(
        "\n".join(
            [
                '_templates_suffix: ".jinja"',
                "_subdirectory: template",
                "",
                "project_name:",
                "  type: str",
                "feature:",
                "  type: str",
            ]
        ),
        encoding="utf-8",
    )
    (template_dir / "{{ project_name }}.txt.jinja").write_text(
        "{{ project_name }}:{{ feature }}",
        encoding="utf-8",
    )

    output_root = tmp_path / "generated"

    generate_project(
        "acme",
        output_root,
        template_root,
        data={"feature": "billing"},
    )

    assert (output_root / "acme.txt").read_text(encoding="utf-8") == "acme:billing"


def test_generate_project_raises_for_missing_template(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError, match="Copier template does not exist"):
        generate_project("acme", tmp_path / "generated", tmp_path / "missing")


def test_get_project_profile_returns_builtin_profile() -> None:
    profile = get_project_profile("python-fastapi-ddd-uv")

    assert profile.toolchain.language == "python"
    assert profile.toolchain.package_manager == "uv"
    assert profile.toolchain.framework == "fastapi"
    assert profile.module_scaffolding == "ddd_context"


def test_generate_project_uses_python_fastapi_ddd_uv_profile(tmp_path: Path) -> None:
    output_root = tmp_path / "generated"

    generate_project("acme", output_root)

    expected_files = [
        "pyproject.toml",
        "README.md",
        ".gitignore",
        ".modwire/project.json",
        "src/acme/__init__.py",
        "src/acme/main.py",
        "src/acme/settings.py",
        "src/acme/cli.py",
        "src/acme/interface/http/router.py",
        "src/acme/infrastructure/clients/generated/.gitkeep",
        "openapi/.gitkeep",
        "tests/test_health.py",
    ]

    for expected_file in expected_files:
        assert (output_root / expected_file).is_file()

    assert not (output_root / "src/acme/bounded_contexts").exists()

    authority = json.loads(
        (output_root / ".modwire/project.json").read_text(encoding="utf-8")
    )
    assert authority["profile"] == "python-fastapi-ddd-uv"
    assert authority["language"] == "python"
    assert authority["language_version"] == "3.13"
    assert authority["package_manager"] == "uv"
    assert authority["framework"] == "fastapi"
    assert authority["architecture"] == "ddd_context"
    assert authority["module_scaffolding"] == "ddd_context"
    assert authority["layout"]["cli"] == "src/acme/cli.py"
    assert authority["layout"]["module_mount"] == "src/acme"
    assert authority["layout"]["generated_clients"] == (
        "src/acme/infrastructure/clients/generated"
    )
    assert "add_context" in authority["operations"]
    assert "add_module" in authority["operations"]
    assert "add_crud_resource" in authority["operations"]
    assert "remove_module" in authority["operations"]
    assert "remove_context" in authority["operations"]

    pyproject = (output_root / "pyproject.toml").read_text(encoding="utf-8")
    assert '"fastapi[standard]"' in pyproject
    assert '"pydantic-settings"' in pyproject
    assert '"typer"' in pyproject
    assert '"pytest"' in pyproject
    assert '"ruff"' in pyproject
    assert '"mypy"' in pyproject
    assert '"openapi-python-client"' in pyproject
    assert 'requires-python = ">=3.13"' in pyproject

    for python_file in output_root.rglob("*.py"):
        ast.parse(python_file.read_text(encoding="utf-8"), filename=str(python_file))


def test_generate_project_normalizes_package_name(tmp_path: Path) -> None:
    output_root = tmp_path / "generated"

    generate_project("Acme Billing API", output_root)

    assert (output_root / "src/acme_billing_api/main.py").is_file()

    authority = json.loads(
        (output_root / ".modwire/project.json").read_text(encoding="utf-8")
    )
    assert authority["package_name"] == "acme_billing_api"
    assert authority["layout"]["http_router"] == (
        "src/acme_billing_api/interface/http/router.py"
    )
    assert authority["layout"]["module_mount"] == "src/acme_billing_api"
