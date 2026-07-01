import json
from pathlib import Path

import pytest

from modwire.projects import generate_project, open_project


def test_load_project_authority_reads_generated_project_json(tmp_path: Path) -> None:
    generate_project("acme", tmp_path)
    project = open_project(tmp_path)

    authority = project.authority()

    assert authority.project_name == "acme"
    assert authority.module_mount == "src/acme"
    assert authority.module_scaffolding == "ddd_context"


def test_project_operations_add_context_container(tmp_path: Path) -> None:
    generate_project("acme", tmp_path)
    project = open_project(tmp_path)

    plan = project.add_context("commerce")

    assert plan.operation == "add_context"
    assert plan.dry_run is False
    assert (tmp_path / "src/acme/bounded_contexts/__init__.py").is_file()
    assert (tmp_path / "src/acme/bounded_contexts/commerce/__init__.py").is_file()


def test_project_operations_add_module_reuses_ddd_context_scaffolding(
    tmp_path: Path,
) -> None:
    generate_project("acme", tmp_path)
    project = open_project(tmp_path)

    plan = project.add_module("billing", context_name="commerce")

    assert plan.operation == "add_module"
    module_root = tmp_path / "src/acme/bounded_contexts/commerce/billing"
    assert (module_root / "domain/aggregates/billingaggregate.py").is_file()
    assert (module_root / "application/use_cases/createbilling.py").is_file()
    assert (module_root / "interface/http/billingcontroller.py").is_file()
    assert not (tmp_path / "src/acme/typescript").exists()
    assert not (tmp_path / "src/acme/php").exists()


def test_project_operations_add_module_uses_typescript_profile(
    tmp_path: Path,
) -> None:
    generate_project("acme", tmp_path, profile="typescript-nestjs-ddd-pnpm")
    project = open_project(tmp_path)

    project.add_context("commerce")
    plan = project.add_module("billing", context_name="commerce")

    assert plan.operation == "add_module"
    module_root = tmp_path / "src/bounded_contexts/commerce/billing"
    assert (module_root / "domain/aggregates/BillingAggregate.ts").is_file()
    assert (module_root / "application/use_cases/CreateBilling.ts").is_file()
    assert (module_root / "interface/http/BillingController.ts").is_file()
    assert not (tmp_path / "src/bounded_contexts/__init__.py").exists()
    assert not (module_root / "domain/aggregates/billingaggregate.py").exists()


def test_project_operations_add_module_uses_php_profile(tmp_path: Path) -> None:
    generate_project("acme", tmp_path, profile="php-symfony-ddd-composer")
    project = open_project(tmp_path)

    project.add_context("commerce")
    plan = project.add_module("billing", context_name="commerce")

    assert plan.operation == "add_module"
    module_root = tmp_path / "src/BoundedContexts/Commerce/Billing"
    assert (module_root / "Domain/Aggregates/BillingAggregate.php").is_file()
    assert (module_root / "Application/UseCases/CreateBilling.php").is_file()
    assert (module_root / "Interface/Http/BillingController.php").is_file()
    context_names = {
        context_path.name
        for context_path in (tmp_path / "src/BoundedContexts").iterdir()
        if context_path.is_dir()
    }
    assert "Commerce" in context_names
    assert "commerce" not in context_names
    assert not (module_root / "domain/aggregates/billingaggregate.py").exists()


def test_project_operations_reject_existing_module_without_overwrite(
    tmp_path: Path,
) -> None:
    generate_project("acme", tmp_path)
    project = open_project(tmp_path)
    project.add_module("billing", context_name="commerce")

    with pytest.raises(FileExistsError, match="Generated module path already exists"):
        project.add_module("billing", context_name="commerce")


def test_project_operations_remove_module_and_context(tmp_path: Path) -> None:
    generate_project("acme", tmp_path)
    project = open_project(tmp_path)
    project.add_module("billing", context_name="commerce")
    module_root = tmp_path / "src/acme/bounded_contexts/commerce/billing"

    dry_run = project.remove_module(
        "billing",
        context_name="commerce",
        dry_run=True,
    )

    assert dry_run.dry_run is True
    assert module_root.exists()

    plan = project.remove_module("billing", context_name="commerce")

    assert plan.operation == "remove_module"
    assert not module_root.exists()

    context_root = tmp_path / "src/acme/bounded_contexts/commerce"
    assert context_root.exists()

    project.remove_context("commerce")

    assert not context_root.exists()


def test_project_operations_remove_context_requires_cascade_for_modules(
    tmp_path: Path,
) -> None:
    generate_project("acme", tmp_path)
    project = open_project(tmp_path)
    project.add_module("billing", context_name="commerce")

    with pytest.raises(ValueError, match="Context is not empty"):
        project.remove_context("commerce")

    project.remove_context("commerce", cascade=True)

    assert not (tmp_path / "src/acme/bounded_contexts/commerce").exists()


def test_project_operations_respect_authority_allowed_operations(tmp_path: Path) -> None:
    generate_project("acme", tmp_path)
    _write_authority(tmp_path, {"operations": []})
    project = open_project(tmp_path)

    with pytest.raises(ValueError, match="does not allow 'add_module'"):
        project.add_module("billing")


def _write_authority(project_root: Path, changes: dict[str, object]) -> None:
    authority_path = project_root / ".modwire/project.json"
    authority = json.loads(authority_path.read_text(encoding="utf-8"))
    authority.update(changes)
    authority_path.write_text(json.dumps(authority), encoding="utf-8")
