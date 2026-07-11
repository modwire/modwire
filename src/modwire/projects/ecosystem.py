from __future__ import annotations

from enum import StrEnum
import re
from typing import Literal, Self

from pydantic import field_validator, model_validator

from modwire.shared import ModwireConfigModel, ModwireReportModel


class PackageRole(StrEnum):
    COORDINATOR = "coordinator"
    RUNTIME = "runtime"
    BUILDING_BLOCK = "building_block"
    INTEGRATION = "integration"


class PackageLifecycle(StrEnum):
    ACTIVE = "active"
    INCUBATING = "incubating"
    MAINTENANCE = "maintenance"
    RETIRED = "retired"


class EcosystemPackage(ModwireConfigModel):
    repository: str
    distribution: str
    component: str
    role: PackageRole
    lifecycle: PackageLifecycle
    summary: str
    depends_on: tuple[str, ...] = ()

    @field_validator("repository")
    @classmethod
    def validate_repository(cls, value: str) -> str:
        if value.count("/") != 1 or any(not part for part in value.split("/")):
            raise ValueError("repository must use the owner/name form")
        return value

    @field_validator("distribution", "component", "summary")
    @classmethod
    def validate_non_empty(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("must not be empty")
        return value

    @field_validator("depends_on")
    @classmethod
    def validate_unique_dependencies(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        if len(value) != len(set(value)):
            raise ValueError("dependencies must be unique")
        return value


class ProjectVisibility(StrEnum):
    PUBLIC = "public"
    PRIVATE = "private"


class EcosystemProject(ModwireConfigModel):
    owner: str
    title: str
    number: int
    visibility: ProjectVisibility
    default_package: str
    description: str
    governance_url: str


class WorkflowActions(ModwireConfigModel):
    checkout: str
    setup_python: str
    upload_artifact: str
    download_artifact: str
    publish_pypi: str


class WorkflowContract(ModwireConfigModel):
    contract_ref: str
    ci_entrypoint: str
    release_entrypoint: str
    verify_reusable: str
    release_build_reusable: str
    release_assets_reusable: str
    release_driver: Literal["github_release"]
    release_event: Literal["published"]
    release_tag_pattern: str
    artifact_name: str
    pypi_environment: str
    actions: WorkflowActions

    @field_validator("release_tag_pattern")
    @classmethod
    def validate_release_tag_pattern(cls, value: str) -> str:
        re.compile(value)
        return value


class ProjectFieldType(StrEnum):
    SINGLE_SELECT = "single_select"
    MULTI_SELECT = "multi_select"
    TEXT = "text"
    DATE = "date"
    NUMBER = "number"


class FieldOwner(StrEnum):
    PROJECT = "project"
    ISSUE = "issue"


class FieldVisibility(StrEnum):
    PUBLIC = "public"
    ORGANIZATION = "organization"


class ProjectField(ModwireConfigModel):
    owner: FieldOwner
    type: ProjectFieldType
    description: str | None = None
    visibility: FieldVisibility | None = None
    options: tuple[str, ...] = ()
    source: Literal["packages"] | None = None

    @model_validator(mode="after")
    def validate_options(self) -> Self:
        select_types = {ProjectFieldType.SINGLE_SELECT, ProjectFieldType.MULTI_SELECT}
        if self.source is not None and self.type not in select_types:
            raise ValueError("derived options require a select field")
        if self.source is not None and self.options:
            raise ValueError("use either source or options, not both")
        if self.type in select_types and not (self.source or self.options):
            raise ValueError("select fields require options or a source")
        if self.type not in select_types and self.options:
            raise ValueError("only select fields accept options")
        if len(self.options) != len(set(self.options)):
            raise ValueError("field options must be unique")
        if self.owner is FieldOwner.ISSUE:
            if not self.description or not self.description.strip():
                raise ValueError("issue fields require a description")
            if self.visibility is None:
                raise ValueError("issue fields require visibility")
        elif self.visibility is not None:
            raise ValueError("project fields do not accept visibility")
        return self


class IssueTypeDefinition(ModwireConfigModel):
    description: str
    color: Literal["gray", "blue", "green", "yellow", "orange", "red", "pink", "purple"]


class IssueIntakePolicy(ModwireConfigModel):
    project: str
    required_fields: tuple[str, ...]
    ready_requires: tuple[Literal["assignee", "acceptance_criteria"], ...]
    incomplete_label: str
    agent_must_not_guess: bool


class IssueRelationshipPolicy(ModwireConfigModel):
    dependencies: Literal["native"]
    hierarchy: Literal["native_sub_issues"]
    cross_repository_parent: Literal["modwire/modwire"]


class ProjectView(ModwireConfigModel):
    name: str
    layout: Literal["board", "roadmap", "table"]
    filter: str | None = None
    group_by: str | None = None
    slice_by: str | None = None


class RepositoryLabel(ModwireConfigModel):
    color: str
    description: str

    @field_validator("color")
    @classmethod
    def validate_color(cls, value: str) -> str:
        value = value.removeprefix("#").lower()
        if len(value) != 6 or any(character not in "0123456789abcdef" for character in value):
            raise ValueError("color must be a six-digit hexadecimal value")
        return value


class ProjectAutomation(ModwireConfigModel):
    auto_add_filter: str
    added_status: str
    closed_status: str
    merged_status: str
    archive_filter: str


class MilestonePolicy(ModwireConfigModel):
    scope: Literal["repository"]
    naming: str
    close_when_complete: bool
    ecosystem_coordination_field: str
    cross_repository_work: Literal["parent_issue_in_modwire_with_sub_issues"]


class GovernanceCadence(ModwireConfigModel):
    triage: str
    roadmap_review: str
    release_readiness: str
    project_status_update: str


class EcosystemContract(ModwireConfigModel):
    version: Literal[3]
    packages: dict[str, EcosystemPackage]
    project: EcosystemProject
    workflows: WorkflowContract
    issue_types: dict[str, IssueTypeDefinition]
    fields: dict[str, ProjectField]
    issue_intake: IssueIntakePolicy
    relationships: IssueRelationshipPolicy
    views: tuple[ProjectView, ...]
    labels: dict[str, RepositoryLabel]
    automation: ProjectAutomation
    milestones: MilestonePolicy
    cadence: GovernanceCadence

    @model_validator(mode="after")
    def validate_taxonomy(self) -> Self:
        if self.project.default_package not in self.packages:
            raise ValueError("default_package must reference a package")

        repositories = self.repositories()
        components = self.component_options()
        distributions = tuple(package.distribution for package in self.packages.values())
        for name, values in (
            ("repositories", repositories),
            ("components", components),
            ("distributions", distributions),
        ):
            if len(values) != len(set(values)):
                raise ValueError(f"package {name} must be unique")

        for key, package in self.packages.items():
            unknown = set(package.depends_on).difference(self.packages)
            if unknown:
                raise ValueError(f"package {key} has unknown dependencies: {unknown}")
            if key in package.depends_on:
                raise ValueError(f"package {key} cannot depend on itself")

        visited: set[str] = set()
        active: set[str] = set()

        def visit(key: str) -> None:
            if key in active:
                raise ValueError(f"package dependency cycle includes {key}")
            if key in visited:
                return
            active.add(key)
            for dependency in self.packages[key].depends_on:
                visit(dependency)
            active.remove(key)
            visited.add(key)

        for key in self.packages:
            visit(key)

        component = self.fields.get("Component")
        if component is None or component.source != "packages":
            raise ValueError("Component must derive its options from packages")

        required_fields = set(self.issue_intake.required_fields)
        unknown_required = required_fields.difference(self.fields)
        if unknown_required:
            raise ValueError(f"issue intake references unknown fields: {unknown_required}")
        non_issue_fields = {
            name
            for name in required_fields
            if self.fields[name].owner is not FieldOwner.ISSUE
        }
        if non_issue_fields:
            raise ValueError(
                f"issue intake requires project-owned fields: {non_issue_fields}"
            )
        if self.issue_intake.incomplete_label not in self.labels:
            raise ValueError("issue intake incomplete_label must reference a label")
        for required_type in ("Task", "Bug", "Feature"):
            if required_type not in self.issue_types:
                raise ValueError(f"missing required issue type: {required_type}")

        statuses = set(self.field_options("Status"))
        for status in (
            self.automation.added_status,
            self.automation.closed_status,
            self.automation.merged_status,
        ):
            if status not in statuses:
                raise ValueError(f"automation references unknown status: {status}")
        return self

    def repositories(self) -> tuple[str, ...]:
        return tuple(package.repository for package in self.packages.values())

    def component_options(self) -> tuple[str, ...]:
        return tuple(package.component for package in self.packages.values())

    def field_options(self, name: str) -> tuple[str, ...]:
        field = self.fields[name]
        if field.source == "packages":
            return self.component_options()
        return field.options

    def default_repository(self) -> str:
        return self.packages[self.project.default_package].repository

    def project_readme(self) -> str:
        repositories = ", ".join(self.repositories())
        return (
            f"Coordinates {repositories}. Governance and reproducible desired state: "
            f"{self.project.governance_url}"
        )


class EcosystemDrift(ModwireReportModel):
    errors: tuple[str, ...] = ()
    manual_controls: tuple[str, ...] = ()

    def is_clean(self) -> bool:
        return not self.errors
