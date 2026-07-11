from __future__ import annotations

from datetime import date
from enum import StrEnum
import re
from typing import Literal, Self

from pydantic import Field, field_validator, model_validator

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


class PackageDependency(ModwireConfigModel):
    specifier: str
    minimum: str

    @field_validator("specifier")
    @classmethod
    def validate_specifier(cls, value: str) -> str:
        value = value.strip()
        if not value or any(character.isspace() for character in value):
            raise ValueError("specifier must be a non-empty PEP 440 constraint")
        return value

    @field_validator("minimum")
    @classmethod
    def validate_minimum(cls, value: str) -> str:
        value = value.strip()
        if not re.fullmatch(r"(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)", value):
            raise ValueError("minimum must use MAJOR.MINOR.PATCH")
        return value

    @model_validator(mode="after")
    def validate_minimum_is_declared(self) -> Self:
        if f">={self.minimum}" not in self.specifier.split(","):
            raise ValueError("specifier must declare the tested minimum with >=")
        return self


class EcosystemPackage(ModwireConfigModel):
    repository: str
    distribution: str
    component: str
    role: PackageRole
    lifecycle: PackageLifecycle
    summary: str
    dependencies: dict[str, PackageDependency] = Field(default_factory=dict)

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
    compatibility_entrypoint: str
    compatibility_schedule: str
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
    TEXT = "text"
    DATE = "date"
    NUMBER = "number"


class ProjectField(ModwireConfigModel):
    type: ProjectFieldType
    options: tuple[str, ...] = ()
    source: Literal["packages", "release_trains"] | None = None

    @model_validator(mode="after")
    def validate_options(self) -> Self:
        if self.source is not None and self.type is not ProjectFieldType.SINGLE_SELECT:
            raise ValueError("derived options require a single_select field")
        if self.source is not None and self.options:
            raise ValueError("use either source or options, not both")
        if self.type is ProjectFieldType.SINGLE_SELECT and not (
            self.source or self.options
        ):
            raise ValueError("single_select fields require options or a source")
        if self.type is not ProjectFieldType.SINGLE_SELECT and self.options:
            raise ValueError("only single_select fields accept options")
        if len(self.options) != len(set(self.options)):
            raise ValueError("field options must be unique")
        return self


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


class CompatibilityResolution(StrEnum):
    MINIMUM = "minimum"
    LATEST = "latest"


class CompatibilityProfile(ModwireConfigModel):
    python_version: str
    resolution: CompatibilityResolution


class CompatibilityPolicy(ModwireConfigModel):
    profiles: dict[str, CompatibilityProfile]
    dependency_changes: Literal["consumer_pull_request"]
    breaking_changes: Literal["coordinated_release_train"]

    @model_validator(mode="after")
    def validate_profiles(self) -> Self:
        resolutions = {profile.resolution for profile in self.profiles.values()}
        if len(self.profiles) != 2 or resolutions != {
            CompatibilityResolution.MINIMUM,
            CompatibilityResolution.LATEST,
        }:
            raise ValueError("compatibility profiles must cover minimum and latest")
        return self


class ReleaseTrainStatus(StrEnum):
    PLANNED = "planned"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ReleasePhase(ModwireConfigModel):
    name: str
    packages: tuple[str, ...]

    @field_validator("packages")
    @classmethod
    def validate_unique_packages(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        if not value or len(value) != len(set(value)):
            raise ValueError("release phase packages must be non-empty and unique")
        return value


class ReleaseTrain(ModwireConfigModel):
    status: ReleaseTrainStatus
    target_date: date | None = None
    summary: str
    phases: tuple[ReleasePhase, ...]
    gates: tuple[
        Literal[
            "package_ci",
            "minimum_compatibility",
            "latest_compatibility",
            "release_readiness",
        ],
        ...,
    ]

    @field_validator("gates")
    @classmethod
    def validate_unique_gates(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        required = {
            "package_ci",
            "minimum_compatibility",
            "latest_compatibility",
            "release_readiness",
        }
        if len(value) != len(set(value)) or set(value) != required:
            raise ValueError("release train must declare every required gate once")
        return value


class EcosystemContract(ModwireConfigModel):
    version: Literal[3]
    packages: dict[str, EcosystemPackage]
    project: EcosystemProject
    workflows: WorkflowContract
    compatibility: CompatibilityPolicy
    release_trains: dict[str, ReleaseTrain]
    fields: dict[str, ProjectField]
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
            unknown = set(package.dependencies).difference(self.packages)
            if unknown:
                raise ValueError(f"package {key} has unknown dependencies: {unknown}")
            if key in package.dependencies:
                raise ValueError(f"package {key} cannot depend on itself")

        visited: set[str] = set()
        active: set[str] = set()

        def visit(key: str) -> None:
            if key in active:
                raise ValueError(f"package dependency cycle includes {key}")
            if key in visited:
                return
            active.add(key)
            for dependency in self.packages[key].dependencies:
                visit(dependency)
            active.remove(key)
            visited.add(key)

        for key in self.packages:
            visit(key)

        if not self.release_trains:
            raise ValueError("at least one release train must be declared")
        for train_name, train in self.release_trains.items():
            phase_by_package: dict[str, int] = {}
            for phase_number, phase in enumerate(train.phases):
                for package in phase.packages:
                    if package not in self.packages:
                        raise ValueError(
                            f"release train {train_name} references unknown package {package}"
                        )
                    if package in phase_by_package:
                        raise ValueError(
                            f"release train {train_name} repeats package {package}"
                        )
                    phase_by_package[package] = phase_number
            for package, phase_number in phase_by_package.items():
                for dependency in self.packages[package].dependencies:
                    dependency_phase = phase_by_package.get(dependency)
                    if dependency_phase is not None and dependency_phase >= phase_number:
                        raise ValueError(
                            f"release train {train_name} must place dependency {dependency} "
                            f"before consumer {package}"
                        )

        component = self.fields.get("Component")
        if component is None or component.source != "packages":
            raise ValueError("Component must derive its options from packages")

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
        if field.source == "release_trains":
            return tuple(self.release_trains)
        return field.options

    def dependency_matrix(self) -> tuple[dict[str, str], ...]:
        return tuple(
            {
                "consumer": consumer,
                "dependency": dependency,
                "specifier": requirement.specifier,
                "minimum": requirement.minimum,
            }
            for consumer, package in self.packages.items()
            for dependency, requirement in package.dependencies.items()
        )

    def github_compatibility_matrix(self) -> dict[str, list[dict[str, str]]]:
        include: list[dict[str, str]] = []
        default = self.project.default_package
        for consumer, package in self.packages.items():
            if package.lifecycle is not PackageLifecycle.ACTIVE or not package.dependencies:
                continue
            for name, profile in self.compatibility.profiles.items():
                if profile.resolution is CompatibilityResolution.MINIMUM:
                    requirements = " ".join(
                        f"{self.packages[key].distribution}=={requirement.minimum}"
                        for key, requirement in package.dependencies.items()
                    )
                else:
                    requirements = " ".join(
                        f"{self.packages[key].distribution}{requirement.specifier}"
                        for key, requirement in package.dependencies.items()
                    )
                include.append(
                    {
                        "consumer": consumer,
                        "profile": name,
                        "python-version": profile.python_version,
                        "repository": package.repository,
                        "working-directory": "." if consumer == default else "consumer",
                        "requirements": requirements,
                    }
                )
        return {"include": include}

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
