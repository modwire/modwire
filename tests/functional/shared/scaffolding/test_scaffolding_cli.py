from pathlib import Path

from tests.functional.cli_helpers import run_cli


def create_scaffold(root: Path) -> Path:
    scaffold = root / "scaffolds" / "basic"
    templates = scaffold / "templates" / "{{ module_name }}"
    templates.mkdir(parents=True)
    (scaffold / "copier.yml").write_text(
        "\n".join(
            [
                '_min_copier_version: "9.0.0"',
                '_templates_suffix: ".jinja"',
                "_subdirectory: templates",
                "",
                "module_name:",
                "  type: str",
                "  default: sample",
                "",
                "service_name:",
                "  type: str",
                "  default: SampleService",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (templates / "service.py.jinja").write_text(
        "class {{ service_name }}:\n"
        "    module = {{ module_name|to_json }}\n",
        encoding="utf-8",
    )
    return scaffold


def test_generates_scaffold_from_cli_data(tmp_path: Path):
    create_scaffold(tmp_path)

    result = run_cli(
        [
            "tools",
            "scaffolding",
            "generate",
            "scaffolds/basic",
            "generated",
            "--data",
            "module_name=billing",
            "--data",
            "service_name=BillingService",
        ],
        tmp_path,
    )

    assert result.exit_code == 0
    assert "Generated scaffold scaffolds/basic at generated" in result.output
    assert (tmp_path / "generated" / "billing" / "service.py").read_text(
        encoding="utf-8"
    ) == ("class BillingService:\n" "    module = \"billing\"\n")


def test_rejects_invalid_cli_data_item(tmp_path: Path):
    create_scaffold(tmp_path)

    result = run_cli(
        [
            "tools",
            "scaffolding",
            "generate",
            "scaffolds/basic",
            "generated",
            "--data",
            "module_name",
        ],
        tmp_path,
    )

    assert result.exit_code != 0
    assert "Invalid data item 'module_name'. Expected key=value." in result.output


def test_generates_bundled_scaffold(tmp_path: Path):
    result = run_cli(
        [
            "tools",
            "scaffolding",
            "generate",
            "modules/layered",
            "generated",
        ],
        tmp_path,
    )

    assert result.exit_code == 0
    assert (tmp_path / "generated" / "sample_package" / "domain.py").is_file()


def test_generates_hexagonal_python_files_with_default_filenames(tmp_path: Path):
    result = run_cli(
        [
            "tools",
            "scaffolding",
            "generate",
            "modules/hexagonal",
            "generated",
        ],
        tmp_path,
    )

    assert result.exit_code == 0
    assert (
        tmp_path
        / "generated"
        / "python"
        / "sample_module"
        / "domain"
        / "models"
        / "sample_module_aggregate.py"
    ).is_file()
    assert (
        tmp_path
        / "generated"
        / "python"
        / "sample_module"
        / "adapters"
        / "inbound"
        / "sample_module_service.py"
    ).is_file()
    assert not list((tmp_path / "generated" / "python").rglob(".py"))


def test_generates_hexagonal_php_namespace_from_shared_data(tmp_path: Path):
    result = run_cli(
        [
            "tools",
            "scaffolding",
            "generate",
            "modules/hexagonal",
            "generated",
            "--data",
            "module_name=orders",
            "--data",
            "module_class_name=Orders",
        ],
        tmp_path,
    )

    assert result.exit_code == 0
    model_file = (
        tmp_path
        / "generated"
        / "php"
        / "src"
        / "Domain"
        / "Models"
        / "OrdersAggregate.php"
    )
    assert "namespace App\\Orders\\Domain\\Models;" in model_file.read_text(
        encoding="utf-8"
    )


def test_generates_composite_design_pattern_for_all_languages(tmp_path: Path):
    result = run_cli(
        [
            "tools",
            "scaffolding",
            "generate",
            "design_patterns/composite",
            "generated",
            "--data",
            "library_package=tree_core",
            "--data",
            "library_namespace=TreeCore",
        ],
        tmp_path,
    )

    assert result.exit_code == 0
    assert (
        tmp_path / "generated" / "python" / "tree_core" / "component.py"
    ).is_file()
    assert (
        tmp_path / "generated" / "python" / "tree_core" / "composite.py"
    ).is_file()
    assert (
        tmp_path
        / "generated"
        / "typescript"
        / "tree_core"
        / "CompositeComponent.ts"
    ).is_file()
    assert (
        tmp_path
        / "generated"
        / "typescript"
        / "tree_core"
        / "CompositeNode.ts"
    ).is_file()
    php_component = (
        tmp_path / "generated" / "php" / "src" / "CompositeComponent.php"
    )
    assert "namespace TreeCore;" in php_component.read_text(encoding="utf-8")


def test_generates_composite_usage_without_regenerating_pattern_library(
    tmp_path: Path,
):
    result = run_cli(
        [
            "tools",
            "scaffolding",
            "generate",
            "design_patterns/composite_usage",
            "generated",
            "--data",
            "package_name=reports",
            "--data",
            "library_package=tree_core",
            "--data",
            "library_namespace=TreeCore",
            "--data",
            "usage_namespace=Reports",
        ],
        tmp_path,
    )

    assert result.exit_code == 0
    python_leaf = (
        tmp_path / "generated" / "python" / "reports" / "leaf.py"
    ).read_text(encoding="utf-8")
    assert "from tree_core.component import CompositeComponent" in python_leaf
    assert not (tmp_path / "generated" / "python" / "tree_core").exists()

    typescript_factory = (
        tmp_path
        / "generated"
        / "typescript"
        / "reports"
        / "SampleCompositeFactory.ts"
    ).read_text(encoding="utf-8")
    assert 'from "tree_core/CompositeNode"' in typescript_factory

    php_leaf = (
        tmp_path / "generated" / "php" / "src" / "TextLeaf.php"
    ).read_text(encoding="utf-8")
    assert "namespace Reports;" in php_leaf
    assert "use TreeCore\\CompositeComponent;" in php_leaf


def test_scaffold_manifests_keep_language_specific_data_in_templates():
    banned_terms = ("php", "python", "typescript", "_file_name")
    manifests = tuple(Path("src/scaffoldings").rglob("copier.yml"))

    assert manifests
    for manifest_path in manifests:
        manifest = manifest_path.read_text(encoding="utf-8").lower()
        for term in banned_terms:
            assert term not in manifest, f"{term!r} leaked into {manifest_path}"


def test_rejects_unknown_bundled_scaffold_id(tmp_path: Path):
    result = run_cli(
        [
            "tools",
            "scaffolding",
            "generate",
            "modules/missing",
            "generated",
        ],
        tmp_path,
    )

    assert result.exit_code != 0
    assert "Unknown scaffold 'modules/missing'" in result.output
    assert "modules/layered" in result.output
    assert "modules/hexagonal" in result.output
    assert "design_patterns/composite" in result.output
    assert "design_patterns/composite_usage" in result.output
