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


def test_hexagonal_manifest_keeps_language_specific_data_in_templates():
    manifest = Path("src/scaffoldings/modules/hexagonal/copier.yml").read_text(
        encoding="utf-8"
    )

    assert "php_" not in manifest
    assert "python_" not in manifest
    assert "typescript_" not in manifest
    assert "_file_name" not in manifest


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
