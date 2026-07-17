from pathlib import Path
import re

import pytest
from pydantic import ValidationError

from modwire_architecture.projects import EcosystemContract, FieldOwner


CONTRACT = Path(__file__).parents[1] / ".github" / "modwire-ecosystem.yml"


def test_ecosystem_contract_is_the_package_taxonomy_source() -> None:
    contract = EcosystemContract.from_yaml(CONTRACT.read_text(encoding="utf-8"))

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
    assert contract.fields["Status"].owner is FieldOwner.PROJECT
    assert contract.fields["Priority"].owner is FieldOwner.ISSUE
    assert contract.issue_intake.required_fields == (
        "Horizon",
        "Priority",
        "Risk",
        "Component",
        "Release train",
        "Effort",
    )
    assert tuple(contract.issue_types) == (
        "Task",
        "Bug",
        "Feature",
        "Epic",
        "Decision",
    )
    assert "modwire/modwire-cli" in contract.project_readme()
    assert re.fullmatch(contract.workflows.release_tag_pattern, "v3.2.1")
    assert not re.fullmatch(contract.workflows.release_tag_pattern, "3.2.1")
    assert not re.fullmatch(contract.workflows.release_tag_pattern, "v3.2")


def test_ecosystem_contract_rejects_taxonomy_drift() -> None:
    contract = EcosystemContract.from_yaml(CONTRACT.read_text(encoding="utf-8"))
    values = contract.to_dict(mode="json")
    values["packages"]["cli"]["component"] = "Core"

    with pytest.raises(ValidationError, match="components must be unique"):
        EcosystemContract.from_dict(values)


def test_ecosystem_contract_rejects_unknown_dependencies() -> None:
    contract = EcosystemContract.from_yaml(CONTRACT.read_text(encoding="utf-8"))
    values = contract.to_dict(mode="json")
    values["packages"]["cli"]["depends_on"] = ["unknown"]

    with pytest.raises(ValidationError, match="unknown dependencies"):
        EcosystemContract.from_dict(values)


def test_issue_intake_rejects_project_owned_required_fields() -> None:
    contract = EcosystemContract.from_yaml(CONTRACT.read_text(encoding="utf-8"))
    values = contract.to_dict(mode="json")
    values["issue_intake"]["required_fields"].append("Status")

    with pytest.raises(ValidationError, match="project-owned fields"):
        EcosystemContract.from_dict(values)


def test_workflow_contract_uses_one_action_set() -> None:
    contract = EcosystemContract.from_yaml(CONTRACT.read_text(encoding="utf-8"))
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
