#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from typing import Any

from modwire.projects import EcosystemContract, EcosystemDrift, ProjectFieldType


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONTRACT = ROOT / ".github" / "modwire-ecosystem.yml"


def gh(*arguments: str) -> str:
    result = subprocess.run(
        ["gh", *arguments],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout


def gh_json(*arguments: str) -> Any:
    return json.loads(gh(*arguments))


def load_contract(path: Path) -> EcosystemContract:
    return EcosystemContract.load_yaml(path)


def project_fields(contract: EcosystemContract) -> dict[str, dict[str, Any]]:
    query = """
    query($id: ID!) {
      node(id: $id) {
        ... on ProjectV2 {
          fields(first: 100) {
            nodes {
              __typename
              ... on ProjectV2Field { id name dataType }
              ... on ProjectV2SingleSelectField { id name options { name } }
            }
          }
        }
      }
    }
    """
    project = gh_json(
        "project",
        "view",
        str(contract.project.number),
        "--owner",
        contract.project.owner,
        "--format",
        "json",
    )
    data = gh_json(
        "api",
        "graphql",
        "-F",
        f"id={project['id']}",
        "-f",
        f"query={query}",
    )
    nodes = data["data"]["node"]["fields"]["nodes"]
    return {node["name"]: node for node in nodes if node.get("name")}


def linked_repositories(contract: EcosystemContract) -> set[str]:
    query = """
    query($id: ID!) {
      node(id: $id) {
        ... on ProjectV2 { repositories(first: 100) { nodes { nameWithOwner } } }
      }
    }
    """
    project = gh_json(
        "project",
        "view",
        str(contract.project.number),
        "--owner",
        contract.project.owner,
        "--format",
        "json",
    )
    data = gh_json(
        "api",
        "graphql",
        "-F",
        f"id={project['id']}",
        "-f",
        f"query={query}",
    )
    nodes = data["data"]["node"]["repositories"]["nodes"]
    return {node["nameWithOwner"] for node in nodes}


def open_work_urls(contract: EcosystemContract) -> set[str]:
    urls: set[str] = set()
    for repository in contract.repositories():
        for kind in ("issue", "pr"):
            items = gh_json(
                kind,
                "list",
                "--repo",
                repository,
                "--state",
                "open",
                "--limit",
                "100",
                "--json",
                "url",
            )
            urls.update(item["url"] for item in items)
    return urls


def project_item_urls(contract: EcosystemContract) -> set[str]:
    data = gh_json(
        "project",
        "item-list",
        str(contract.project.number),
        "--owner",
        contract.project.owner,
        "--limit",
        "1000",
        "--format",
        "json",
    )
    return {
        item["content"]["url"]
        for item in data["items"]
        if item.get("content", {}).get("url")
    }


def label_drift(contract: EcosystemContract) -> list[str]:
    errors: list[str] = []
    for repository in contract.repositories():
        actual = {
            label["name"]: label
            for label in gh_json(
                "label",
                "list",
                "--repo",
                repository,
                "--limit",
                "100",
                "--json",
                "name,color,description",
            )
        }
        for name, expected in contract.labels.items():
            label = actual.get(name)
            if label is None:
                errors.append(f"{repository}: missing label {name}")
                continue
            if label["color"].lower() != expected.color:
                errors.append(f"{repository}: label {name} has the wrong color")
            if label["description"] != expected.description:
                errors.append(f"{repository}: label {name} has the wrong description")
    return errors


def inspect_live(contract: EcosystemContract) -> EcosystemDrift:
    errors: list[str] = []
    project = gh_json(
        "project",
        "view",
        str(contract.project.number),
        "--owner",
        contract.project.owner,
        "--format",
        "json",
    )
    expected_project = {
        "title": contract.project.title,
        "public": contract.project.visibility.value == "public",
        "shortDescription": contract.project.description,
        "readme": contract.project_readme(),
    }
    for name, expected in expected_project.items():
        if project[name] != expected:
            errors.append(f"project {name} differs from the contract")

    expected_repositories = set(contract.repositories())
    actual_repositories = linked_repositories(contract)
    for repository in sorted(expected_repositories - actual_repositories):
        errors.append(f"project is not linked to {repository}")
    for repository in sorted(actual_repositories - expected_repositories):
        errors.append(f"project has unmanaged repository {repository}")

    actual_fields = project_fields(contract)
    for name, expected in contract.fields.items():
        actual = actual_fields.get(name)
        if actual is None:
            errors.append(f"project is missing field {name}")
            continue
        if expected.type is ProjectFieldType.SINGLE_SELECT:
            options = tuple(option["name"] for option in actual.get("options", ()))
            if options != contract.field_options(name):
                errors.append(f"project field {name} options differ from the contract")
        elif actual.get("dataType", "").lower() != expected.type.value:
            errors.append(f"project field {name} type differs from the contract")

    missing_items = open_work_urls(contract) - project_item_urls(contract)
    for url in sorted(missing_items):
        errors.append(f"project is missing open work item {url}")
    errors.extend(label_drift(contract))
    return EcosystemDrift(
        errors=tuple(errors),
        manual_controls=(
            "Saved Project views must be compared in the GitHub UI.",
            "Project auto-add, close, merge, and archive workflows must be compared in the GitHub UI.",
        ),
    )


def apply_live(contract: EcosystemContract) -> None:
    gh(
        "project",
        "edit",
        str(contract.project.number),
        "--owner",
        contract.project.owner,
        "--title",
        contract.project.title,
        "--visibility",
        contract.project.visibility.value.upper(),
        "--description",
        contract.project.description,
        "--readme",
        contract.project_readme(),
    )
    linked = linked_repositories(contract)
    for repository in contract.repositories():
        if repository not in linked:
            gh(
                "project",
                "link",
                str(contract.project.number),
                "--owner",
                contract.project.owner,
                "--repo",
                repository,
            )
        for name, label in contract.labels.items():
            gh(
                "label",
                "create",
                name,
                "--repo",
                repository,
                "--color",
                label.color,
                "--description",
                label.description,
                "--force",
            )

    existing_items = project_item_urls(contract)
    for url in sorted(open_work_urls(contract) - existing_items):
        gh(
            "project",
            "item-add",
            str(contract.project.number),
            "--owner",
            contract.project.owner,
            "--url",
            url,
        )


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description="Validate and reconcile Modwire governance")
    result.add_argument(
        "command",
        choices=("validate", "check-live", "apply-live", "schema"),
        nargs="?",
        default="validate",
    )
    result.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    return result


def main() -> int:
    arguments = parser().parse_args()
    contract = load_contract(arguments.contract)
    if arguments.command == "schema":
        print(json.dumps(EcosystemContract.model_json_schema(), indent=2))
        return 0
    if arguments.command == "validate":
        print(
            f"valid ecosystem contract: {len(contract.packages)} packages, "
            f"{len(contract.fields)} project fields"
        )
        return 0
    if arguments.command == "apply-live":
        apply_live(contract)

    drift = inspect_live(contract)
    print(drift.pretty())
    return 0 if drift.is_clean() else 1


if __name__ == "__main__":
    raise SystemExit(main())
