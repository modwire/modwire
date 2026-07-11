#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path
from typing import Any

from modwire.projects import (
    EcosystemContract,
    EcosystemDrift,
    FieldOwner,
    FieldVisibility,
    ProjectFieldType,
)


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


def gh_api_json(method: str, path: str, payload: dict[str, Any]) -> Any:
    result = subprocess.run(
        [
            "gh",
            "api",
            "--method",
            method,
            "-H",
            "X-GitHub-Api-Version: 2026-03-10",
            "--input",
            "-",
            path,
        ],
        check=True,
        capture_output=True,
        input=json.dumps(payload),
        text=True,
    )
    return json.loads(result.stdout) if result.stdout else None


def load_contract(path: Path) -> EcosystemContract:
    return EcosystemContract.load_yaml(path)


def organization_issue_types(contract: EcosystemContract) -> dict[str, dict[str, Any]]:
    values = gh_json(
        "api",
        "-H",
        "X-GitHub-Api-Version: 2026-03-10",
        f"orgs/{contract.project.owner}/issue-types",
    )
    return {value["name"]: value for value in values}


def organization_issue_fields(contract: EcosystemContract) -> dict[str, dict[str, Any]]:
    values = gh_json(
        "api",
        "-H",
        "X-GitHub-Api-Version: 2026-03-10",
        f"orgs/{contract.project.owner}/issue-fields",
    )
    return {value["name"]: value for value in values}


def option_color(field_name: str, option_name: str, position: int) -> str:
    semantic = {
        "P0": "red",
        "P1": "orange",
        "P2": "yellow",
        "P3": "green",
        "High": "red",
        "Medium": "yellow",
        "Low": "green",
        "Now": "red",
        "Next": "yellow",
        "Later": "blue",
        "Unscheduled": "gray",
        "XS": "green",
        "S": "blue",
        "M": "yellow",
        "L": "orange",
        "XL": "red",
    }
    if option_name in semantic:
        return semantic[option_name]
    component_colors = ("blue", "green", "purple", "orange", "pink", "yellow")
    return component_colors[position % len(component_colors)]


def issue_governance_drift(contract: EcosystemContract) -> list[str]:
    errors: list[str] = []
    actual_types = organization_issue_types(contract)
    for name, expected in contract.issue_types.items():
        actual = actual_types.get(name)
        if actual is None:
            errors.append(f"organization is missing issue type {name}")
            continue
        if not actual.get("is_enabled", True):
            errors.append(f"organization issue type {name} is disabled")
        if actual.get("description") != expected.description:
            errors.append(f"organization issue type {name} description differs")
        if actual.get("color") != expected.color:
            errors.append(f"organization issue type {name} color differs")

    actual_fields = organization_issue_fields(contract)
    for name, expected in contract.fields.items():
        if expected.owner is not FieldOwner.ISSUE:
            continue
        actual = actual_fields.get(name)
        if actual is None:
            errors.append(f"organization is missing issue field {name}")
            continue
        if actual.get("data_type") != expected.type.value:
            errors.append(f"organization issue field {name} type differs")
        expected_visibility = (
            "all"
            if expected.visibility is FieldVisibility.PUBLIC
            else "organization_members_only"
        )
        if actual.get("visibility") != expected_visibility:
            errors.append(f"organization issue field {name} visibility differs")
        if actual.get("description") != expected.description:
            errors.append(f"organization issue field {name} description differs")
        if expected.type in {
            ProjectFieldType.SINGLE_SELECT,
            ProjectFieldType.MULTI_SELECT,
        }:
            actual_options = tuple(option["name"] for option in actual.get("options", ()))
            if actual_options != contract.field_options(name):
                errors.append(f"organization issue field {name} options differ")
    return errors


def desired_issue_field_options(
    contract: EcosystemContract,
    name: str,
    actual: dict[str, Any] | None,
) -> list[dict[str, Any]]:
    existing = {option["name"]: option for option in (actual or {}).get("options", ())}
    aliases = {
        "Priority": {"P0": "Urgent", "P1": "High", "P2": "Medium", "P3": "Low"},
        "Effort": {"S": "Low", "M": "Medium", "L": "High"},
    }
    result: list[dict[str, Any]] = []
    for position, option_name in enumerate(contract.field_options(name), start=1):
        current = existing.get(option_name)
        if current is None:
            current = existing.get(aliases.get(name, {}).get(option_name, ""))
        option: dict[str, Any] = {
            "name": option_name,
            "description": None,
            "color": option_color(name, option_name, position - 1),
            "priority": position,
        }
        if current is not None:
            option["id"] = current["id"]
        result.append(option)
    return result


def apply_issue_governance(contract: EcosystemContract) -> None:
    owner = contract.project.owner
    actual_types = organization_issue_types(contract)
    for name, expected in contract.issue_types.items():
        payload = {
            "name": name,
            "description": expected.description,
            "is_enabled": True,
            "color": expected.color,
        }
        actual = actual_types.get(name)
        if actual is None:
            gh_api_json("POST", f"orgs/{owner}/issue-types", payload)
        else:
            gh_api_json("PATCH", f"orgs/{owner}/issue-types/{actual['id']}", payload)

    actual_fields = organization_issue_fields(contract)
    for name, expected in contract.fields.items():
        if expected.owner is not FieldOwner.ISSUE:
            continue
        actual = actual_fields.get(name)
        if actual is not None and actual.get("data_type") != expected.type.value:
            raise RuntimeError(
                f"cannot change organization issue field {name} from "
                f"{actual.get('data_type')} to {expected.type.value}"
            )
        payload: dict[str, Any] = {
            "name": name,
            "description": expected.description,
            "visibility": (
                "all"
                if expected.visibility is FieldVisibility.PUBLIC
                else "organization_members_only"
            ),
        }
        if expected.type in {
            ProjectFieldType.SINGLE_SELECT,
            ProjectFieldType.MULTI_SELECT,
        }:
            payload["options"] = desired_issue_field_options(contract, name, actual)
        if actual is None:
            payload["data_type"] = expected.type.value
            gh_api_json("POST", f"orgs/{owner}/issue-fields", payload)
        else:
            gh_api_json("PATCH", f"orgs/{owner}/issue-fields/{actual['id']}", payload)


def workflow_drift(contract: EcosystemContract) -> list[str]:
    errors: list[str] = []
    workflow_paths = (
        contract.workflows.ci_entrypoint,
        contract.workflows.release_entrypoint,
        contract.workflows.verify_reusable,
        contract.workflows.release_build_reusable,
        contract.workflows.release_assets_reusable,
    )
    contents: dict[str, str] = {}
    for relative_path in workflow_paths:
        path = ROOT / relative_path
        if not path.is_file():
            errors.append(f"missing workflow file {relative_path}")
            continue
        contents[relative_path] = path.read_text(encoding="utf-8")

    expected_actions = {
        "actions/checkout": contract.workflows.actions.checkout,
        "actions/setup-python": contract.workflows.actions.setup_python,
        "actions/upload-artifact": contract.workflows.actions.upload_artifact,
        "actions/download-artifact": contract.workflows.actions.download_artifact,
        "pypa/gh-action-pypi-publish": contract.workflows.actions.publish_pypi,
    }
    for path in sorted((ROOT / ".github" / "workflows").glob("*.yml")):
        text = path.read_text(encoding="utf-8")
        for action in re.findall(
            r"(?:actions/(?:checkout|setup-python|upload-artifact|download-artifact)|"
            r"pypa/gh-action-pypi-publish)@[^\s]+",
            text,
        ):
            name = action.split("@", maxsplit=1)[0]
            if action != expected_actions[name]:
                errors.append(f"{path.name}: unmanaged action reference {action}")

    release = contents.get(contract.workflows.release_entrypoint, "")
    release_build = contents.get(contract.workflows.release_build_reusable, "")
    verify = contents.get(contract.workflows.verify_reusable, "")
    required_references = {
        contract.workflows.release_entrypoint: (
            contract.workflows.release_build_reusable,
            contract.workflows.release_assets_reusable,
            contract.workflows.actions.download_artifact,
            contract.workflows.actions.publish_pypi,
        ),
        contract.workflows.release_build_reusable: (
            contract.workflows.actions.checkout,
            contract.workflows.actions.setup_python,
            contract.workflows.actions.upload_artifact,
        ),
        contract.workflows.verify_reusable: (
            contract.workflows.actions.checkout,
            contract.workflows.actions.setup_python,
            contract.workflows.actions.upload_artifact,
        ),
        contract.workflows.release_assets_reusable: (
            contract.workflows.actions.download_artifact,
        ),
    }
    for path, references in required_references.items():
        text = contents.get(path, "")
        for reference in references:
            if reference not in text:
                errors.append(f"{path}: missing required reference {reference}")

    for forbidden in (
        "python - <<",
        "SETUPTOOLS_SCM_PRETEND_VERSION",
        "softprops/",
    ):
        if forbidden in release or forbidden in release_build:
            errors.append(f"release workflows contain forbidden pattern {forbidden}")
    if contract.workflows.artifact_name not in release or contract.workflows.artifact_name not in release_build:
        errors.append("release artifact name differs from the workflow contract")
    release_assets = contents.get(contract.workflows.release_assets_reusable, "")
    if (
        "workflow_call:" not in verify
        or "workflow_call:" not in release_build
        or "workflow_call:" not in release_assets
    ):
        errors.append("reusable workflows must use workflow_call")
    if "release:" not in release or "types: [published]" not in release:
        errors.append("release.yml must be driven by a published GitHub Release")
    if "skip-existing: true" not in release:
        errors.append("release.yml must make PyPI publication idempotent")
    if '--repo "$GITHUB_REPOSITORY"' not in release_assets:
        errors.append("release assets must target GITHUB_REPOSITORY explicitly")
    return errors


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
    errors = workflow_drift(contract)
    errors.extend(issue_governance_drift(contract))
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
            "Issue fields must be pinned and ordered for every issue type in the organization UI.",
            "Legacy Project-only field values must be migrated before deleting duplicate fields.",
        ),
    )


def apply_live(contract: EcosystemContract) -> None:
    apply_issue_governance(contract)
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
        errors = workflow_drift(contract)
        if errors:
            print(EcosystemDrift(errors=tuple(errors)).pretty())
            return 1
        print(
            f"valid ecosystem contract: {len(contract.packages)} packages, "
            f"{sum(field.owner is FieldOwner.PROJECT for field in contract.fields.values())} "
            "Project-owned field, "
            f"{sum(field.owner is FieldOwner.ISSUE for field in contract.fields.values())} "
            "issue-owned fields"
        )
        return 0
    if arguments.command == "apply-live":
        apply_live(contract)

    drift = inspect_live(contract)
    print(drift.pretty())
    return 0 if drift.is_clean() else 1


if __name__ == "__main__":
    raise SystemExit(main())
