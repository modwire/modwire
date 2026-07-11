from pathlib import Path

import pytest
from pydantic import ValidationError

from modwire.projects import EcosystemContract


CONTRACT = Path(__file__).parents[1] / ".github" / "modwire-ecosystem.yml"


def test_ecosystem_contract_is_the_package_taxonomy_source() -> None:
    contract = EcosystemContract.load_yaml(CONTRACT)

    assert contract.repositories() == (
        "9orky/modwire",
        "9orky/modwire-cli",
        "9orky/modwire-extraction",
        "9orky/modwire-mermaid",
        "9orky/modwire-siren",
        "9orky/modwire-mcp",
    )
    assert contract.field_options("Component") == (
        "Core",
        "CLI",
        "Extraction",
        "Mermaid",
        "Siren",
        "MCP",
    )
    assert contract.default_repository() == "9orky/modwire"
    assert "9orky/modwire-cli" in contract.project_readme()


def test_ecosystem_contract_rejects_taxonomy_drift() -> None:
    contract = EcosystemContract.load_yaml(CONTRACT)
    values = contract.to_dict(mode="json")
    values["packages"]["cli"]["component"] = "Core"

    with pytest.raises(ValidationError, match="components must be unique"):
        EcosystemContract.from_dict(values)


def test_ecosystem_contract_rejects_unknown_dependencies() -> None:
    contract = EcosystemContract.load_yaml(CONTRACT)
    values = contract.to_dict(mode="json")
    values["packages"]["cli"]["depends_on"] = ["unknown"]

    with pytest.raises(ValidationError, match="unknown dependencies"):
        EcosystemContract.from_dict(values)
