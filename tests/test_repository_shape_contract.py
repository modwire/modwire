from pathlib import Path

from pydantic_yaml import parse_yaml_raw_as


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "docs" / "scaffolding" / "repository-contract-v1.yaml"
GOLDEN_PATH = ROOT / "docs" / "scaffolding" / "golden"


def load_yaml(path: Path) -> dict:
    return parse_yaml_raw_as(dict, path.read_text(encoding="utf-8"))


def test_repository_contract_orders_uv_before_modwire():
    contract = load_yaml(CONTRACT_PATH)

    assert contract["schema_version"] == 1
    assert [step["scaffold"] for step in contract["pipeline"]] == [
        "uv-package",
        "modwire-repository",
    ]
    assert contract["module_policy"]["reserved_module"] == "shared"
    assert contract["module_policy"]["required_modules"] == ["shared"]
    assert contract["module_policy"]["shared_dependencies"] == []
    assert contract["adoption"]["preserve_application_code"] is True
    assert contract["apply"]["second_run_writes"] == 0


def test_golden_shapes_cover_each_repository_kind():
    contract = load_yaml(CONTRACT_PATH)
    goldens = [load_yaml(path) for path in sorted(GOLDEN_PATH.glob("*.yaml"))]

    assert {golden["variables"]["repository_kind"] for golden in goldens} == set(
        contract["repository_kinds"]
    )
    for golden in goldens:
        variables = golden["variables"]
        assert set(contract["variables"]["required"]) <= set(variables)
        shared = next(module for module in variables["modules"] if module["name"] == "shared")
        assert shared["dependencies"] == []
        paths = [entry["path"] for entry in golden["expected_paths"]]
        assert len(paths) == len(set(paths))
        assert ".modwire/repository.yaml" in paths
