from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class ProjectLayout(BaseModel):
    model_config = ConfigDict(frozen=True, from_attributes=True)

    package_root: str
    cli: str
    http_router: str
    module_mount: str
    generated_clients: str
    openapi: str
    tests: str

    def resolve(self, package_name: str) -> "ProjectLayout":
        return ProjectLayout(
            package_root=self.package_root.format(package_name=package_name),
            cli=self.cli.format(package_name=package_name),
            http_router=self.http_router.format(package_name=package_name),
            module_mount=self.module_mount.format(package_name=package_name),
            generated_clients=self.generated_clients.format(package_name=package_name),
            openapi=self.openapi.format(package_name=package_name),
            tests=self.tests.format(package_name=package_name),
        )


class ProjectModuleLayout(BaseModel):
    model_config = ConfigDict(frozen=True, from_attributes=True)

    context_root: str
    module_root: str
    context_marker_roots: tuple[str, ...] = ()
    scaffold_output_roots: dict[str, str] = Field(default_factory=dict)
    package_markers: dict[str, tuple[str, ...]] = Field(default_factory=dict)

    def resolve(self, module_mount: str) -> "ProjectModuleLayout":
        return ProjectModuleLayout(
            context_root=self.context_root.replace("{module_mount}", module_mount),
            module_root=self.module_root.replace("{module_mount}", module_mount),
            context_marker_roots=tuple(
                marker_root.replace("{module_mount}", module_mount)
                for marker_root in self.context_marker_roots
            ),
            scaffold_output_roots=dict(self.scaffold_output_roots),
            package_markers=dict(self.package_markers),
        )


class ProjectToolchain(BaseModel):
    model_config = ConfigDict(frozen=True, from_attributes=True)

    language: str
    language_version: str
    package_manager: str
    framework: str
    dependencies: tuple[str, ...] = ()
    dev_dependencies: tuple[str, ...] = ()
    scripts: dict[str, str] = Field(default_factory=dict)


class ProjectProfile(BaseModel):
    model_config = ConfigDict(frozen=True, from_attributes=True)

    name: str
    architecture: str
    module_scaffolding: str
    toolchain: ProjectToolchain
    layout: ProjectLayout
    module_layout: ProjectModuleLayout
    operations: tuple[str, ...] = ()

    def resolved_authority(self, project_name: str, package_name: str) -> dict[str, object]:
        layout = self.layout.resolve(package_name)
        return {
            "project_name": project_name,
            "package_name": package_name,
            "profile": self.name,
            "language": self.toolchain.language,
            "language_version": self.toolchain.language_version,
            "package_manager": self.toolchain.package_manager,
            "framework": self.toolchain.framework,
            "architecture": self.architecture,
            "module_scaffolding": self.module_scaffolding,
            "dependencies": list(self.toolchain.dependencies),
            "dev_dependencies": list(self.toolchain.dev_dependencies),
            "scripts": dict(self.toolchain.scripts),
            "layout": layout.model_dump(mode="json"),
            "module_layout": self.module_layout.resolve(
                layout.module_mount,
            ).model_dump(mode="json"),
            "operations": list(self.operations),
        }


PYTHON_FASTAPI_DDD_UV = ProjectProfile(
    name="python-fastapi-ddd-uv",
    architecture="ddd_context",
    module_scaffolding="ddd_context",
    toolchain=ProjectToolchain(
        language="python",
        language_version="3.13",
        package_manager="uv",
        framework="fastapi",
        dependencies=(
            "fastapi[standard]",
            "pydantic-settings",
            "typer",
        ),
        dev_dependencies=(
            "pytest",
            "ruff",
            "mypy",
            "openapi-python-client",
        ),
        scripts={
            "dev": "fastapi dev src/{package_name}/main.py",
            "test": "pytest",
            "lint": "ruff check .",
            "typecheck": "mypy src",
            "openapi-client": (
                "openapi-python-client generate --path openapi/openapi.yaml "
                "--output-path src/{package_name}/infrastructure/clients/generated"
            ),
        },
    ),
    layout=ProjectLayout(
        package_root="src/{package_name}",
        cli="src/{package_name}/cli.py",
        http_router="src/{package_name}/interface/http/router.py",
        module_mount="src/{package_name}",
        generated_clients="src/{package_name}/infrastructure/clients/generated",
        openapi="openapi",
        tests="tests",
    ),
    module_layout=ProjectModuleLayout(
        context_root="{module_mount}/bounded_contexts/{context_name}",
        module_root="{module_mount}/bounded_contexts/{context_name}/{module_name}",
        context_marker_roots=(
            "{module_mount}/bounded_contexts",
            "{module_mount}/bounded_contexts/{context_name}",
        ),
        scaffold_output_roots={
            "python": "python",
            "typescript": "typescript",
            "php": "php",
        },
        package_markers={
            "python": ("__init__.py",),
        },
    ),
    operations=(
        "add_context",
        "add_module",
        "add_crud_resource",
        "add_use_case",
        "remove_module",
        "remove_context",
        "remove_resource",
        "add_openapi_client",
    ),
)


TYPESCRIPT_NESTJS_DDD_PNPM = ProjectProfile(
    name="typescript-nestjs-ddd-pnpm",
    architecture="ddd_context",
    module_scaffolding="ddd_context",
    toolchain=ProjectToolchain(
        language="typescript",
        language_version="5",
        package_manager="pnpm",
        framework="nestjs",
        dependencies=(
            "@nestjs/common",
            "@nestjs/core",
            "@nestjs/platform-express",
            "reflect-metadata",
            "rxjs",
        ),
        dev_dependencies=(
            "@nestjs/cli",
            "@nestjs/testing",
            "@types/jest",
            "@types/node",
            "jest",
            "prettier",
            "ts-jest",
            "ts-node",
            "typescript",
        ),
        scripts={
            "dev": "nest start --watch",
            "build": "nest build",
            "test": "jest",
            "lint": "prettier --check \"src/**/*.ts\" \"test/**/*.ts\"",
            "openapi-client": (
                "openapi-generator-cli generate -i openapi/openapi.yaml "
                "-g typescript-fetch -o src/infrastructure/clients/generated"
            ),
        },
    ),
    layout=ProjectLayout(
        package_root="src",
        cli="src/main.ts",
        http_router="src/app.module.ts",
        module_mount="src",
        generated_clients="src/infrastructure/clients/generated",
        openapi="openapi",
        tests="test",
    ),
    module_layout=ProjectModuleLayout(
        context_root="{module_mount}/bounded_contexts/{context_name}",
        module_root="{module_mount}/bounded_contexts/{context_name}/{module_name}",
        scaffold_output_roots={
            "typescript": "typescript",
        },
    ),
    operations=(
        "add_context",
        "add_module",
        "add_crud_resource",
        "add_use_case",
        "remove_module",
        "remove_context",
        "remove_resource",
        "add_openapi_client",
    ),
)


PHP_SYMFONY_DDD_COMPOSER = ProjectProfile(
    name="php-symfony-ddd-composer",
    architecture="ddd_context",
    module_scaffolding="ddd_context",
    toolchain=ProjectToolchain(
        language="php",
        language_version="8.2",
        package_manager="composer",
        framework="symfony",
        dependencies=(
            "php:^8.2",
            "symfony/console",
            "symfony/dotenv",
            "symfony/framework-bundle",
            "symfony/runtime",
            "symfony/serializer",
            "symfony/validator",
            "symfony/yaml",
        ),
        dev_dependencies=(
            "phpunit/phpunit",
            "friendsofphp/php-cs-fixer",
            "phpstan/phpstan",
        ),
        scripts={
            "dev": "symfony server:start",
            "test": "phpunit",
            "lint": "php-cs-fixer fix --dry-run --diff",
            "typecheck": "phpstan analyse src",
            "openapi-client": (
                "openapi-generator-cli generate -i openapi/openapi.yaml "
                "-g php -o src/Infrastructure/Clients/Generated"
            ),
        },
    ),
    layout=ProjectLayout(
        package_root="src",
        cli="bin/console",
        http_router="config/routes.yaml",
        module_mount="src",
        generated_clients="src/Infrastructure/Clients/Generated",
        openapi="openapi",
        tests="tests",
    ),
    module_layout=ProjectModuleLayout(
        context_root="{module_mount}/BoundedContexts/{context_class_name}",
        module_root=(
            "{module_mount}/BoundedContexts/{context_class_name}/{module_class_name}"
        ),
        scaffold_output_roots={
            "php": "php/src",
        },
    ),
    operations=(
        "add_context",
        "add_module",
        "add_crud_resource",
        "add_use_case",
        "remove_module",
        "remove_context",
        "remove_resource",
        "add_openapi_client",
    ),
)


PROJECT_PROFILES: dict[str, ProjectProfile] = {
    PYTHON_FASTAPI_DDD_UV.name: PYTHON_FASTAPI_DDD_UV,
    TYPESCRIPT_NESTJS_DDD_PNPM.name: TYPESCRIPT_NESTJS_DDD_PNPM,
    PHP_SYMFONY_DDD_COMPOSER.name: PHP_SYMFONY_DDD_COMPOSER,
}


def get_project_profile(name: str) -> ProjectProfile:
    try:
        return PROJECT_PROFILES[name]
    except KeyError as error:
        known_profiles = ", ".join(sorted(PROJECT_PROFILES))
        raise KeyError(f"Unknown project profile: {name}. Known profiles: {known_profiles}") from error


__all__ = [
    "PROJECT_PROFILES",
    "ProjectLayout",
    "ProjectModuleLayout",
    "ProjectProfile",
    "ProjectToolchain",
    "get_project_profile",
]
