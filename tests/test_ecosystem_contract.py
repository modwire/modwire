from pathlib import Path
import re

import pytest
from pydantic import ValidationError

from modwire.projects import EcosystemContract


CONTRACT = Path(__file__).parents[1] / ".github" / "modwire-ecosystem.yml"


def test_ecosystem_contract_is_the_package_taxonomy_source() -> None:
    contract = EcosystemContract.load_yaml(CONTRACT)

    assert contract.repositories() == (
        "modwire/modwire",
        "modwire/modwire-cli",
        "modwire/modwire-extraction",
        "modwire/modwire-mermaid",
        "modwire/modwire-siren",
        "modwire/modwire-mcp",
    )
    assert contract.field_options("Component") == (
        "Core",
        "CLI",
        "Extraction",
        "Mermaid",
        "Siren",
        "MCP",
    )
    assert contract.default_repository() == "modwire/modwire"
    assert contract.field_options("Release train") == (
        "workflows-v1 adoption",
        "2026-Q3 Contracts",
    )
    assert contract.dependency_matrix() == (
        {
            "consumer": "core",
            "dependency": "extraction",
            "specifier": ">=1.0.2,<2.0.0",
            "minimum": "1.0.2",
        },
        {
            "consumer": "core",
            "dependency": "mermaid",
            "specifier": ">=1.0.0,<2.0.0",
            "minimum": "1.0.0",
        },
        {
            "consumer": "core",
            "dependency": "siren",
            "specifier": ">=1.0.0,<2.0.0",
            "minimum": "1.0.0",
        },
        {
            "consumer": "cli",
            "dependency": "core",
            "specifier": ">=4.0.2,<5.0.0",
            "minimum": "4.0.2",
        },
        {
            "consumer": "mcp",
            "dependency": "extraction",
            "specifier": ">=1.0.2,<2.0.0",
            "minimum": "1.0.2",
        },
    )
    assert "modwire/modwire-cli" in contract.project_readme()
    assert re.fullmatch(contract.workflows.release_tag_pattern, "v3.2.1")
    assert not re.fullmatch(contract.workflows.release_tag_pattern, "3.2.1")
    assert not re.fullmatch(contract.workflows.release_tag_pattern, "v3.2")


def test_ecosystem_contract_rejects_taxonomy_drift() -> None:
    contract = EcosystemContract.load_yaml(CONTRACT)
    values = contract.to_dict(mode="json")
    values["packages"]["cli"]["component"] = "Core"

    with pytest.raises(ValidationError, match="components must be unique"):
        EcosystemContract.from_dict(values)


def test_ecosystem_contract_rejects_unknown_dependencies() -> None:
    contract = EcosystemContract.load_yaml(CONTRACT)
    values = contract.to_dict(mode="json")
    values["packages"]["cli"]["dependencies"]["unknown"] = {
        "specifier": ">=1.0.0",
        "minimum": "1.0.0",
    }

    with pytest.raises(ValidationError, match="unknown dependencies"):
        EcosystemContract.from_dict(values)


def test_release_train_must_follow_dependency_order() -> None:
    contract = EcosystemContract.load_yaml(CONTRACT)
    values = contract.to_dict(mode="json")
    phases = values["release_trains"]["2026-Q3 Contracts"]["phases"]
    phases[0]["packages"] = ["core"]
    phases[1]["packages"] = ["extraction", "mermaid", "siren"]

    with pytest.raises(ValidationError, match="before consumer core"):
        EcosystemContract.from_dict(values)


def test_github_matrix_is_derived_from_default_package_dependencies() -> None:
    contract = EcosystemContract.load_yaml(CONTRACT)

    assert contract.github_compatibility_matrix() == {
        "include": [
            {
                "consumer": "core",
                "profile": "minimum",
                "python-version": "3.12",
                "repository": "modwire/modwire",
                "working-directory": ".",
                "requirements": (
                    "modwire-extraction==1.0.2 "
                    "modwire-mermaid==1.0.0 modwire-siren==1.0.0"
                ),
            },
            {
                "consumer": "core",
                "profile": "latest",
                "python-version": "3.14",
                "repository": "modwire/modwire",
                "working-directory": ".",
                "requirements": (
                    "modwire-extraction>=1.0.2,<2.0.0 "
                    "modwire-mermaid>=1.0.0,<2.0.0 "
                    "modwire-siren>=1.0.0,<2.0.0"
                ),
            },
            {
                "consumer": "cli",
                "profile": "minimum",
                "python-version": "3.12",
                "repository": "modwire/modwire-cli",
                "working-directory": "consumer",
                "requirements": "modwire==4.0.2",
            },
            {
                "consumer": "cli",
                "profile": "latest",
                "python-version": "3.14",
                "repository": "modwire/modwire-cli",
                "working-directory": "consumer",
                "requirements": "modwire>=4.0.2,<5.0.0",
            },
        ]
    }


def test_workflow_contract_uses_one_action_set() -> None:
    contract = EcosystemContract.load_yaml(CONTRACT)
    workflows = Path(__file__).parents[1] / ".github" / "workflows"
    contents = "\n".join(
        path.read_text(encoding="utf-8") for path in workflows.glob("*.yml")
    )

    for action in contract.workflows.actions.to_dict().values():
        assert action in contents
    assert "python - <<" not in contents
    assert "SETUPTOOLS_SCM_PRETEND_VERSION" not in contents
    assert "softprops/" not in contents
    assert '--repo "$GITHUB_REPOSITORY"' in contents
