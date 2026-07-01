from pathlib import Path

import pytest

from modwire.modules import generate_module


def test_generate_module_uses_caller_copier_template(tmp_path: Path) -> None:
    template_root = tmp_path / "template-root"
    template_dir = template_root / "template"
    template_dir.mkdir(parents=True)
    (template_root / "copier.yml").write_text(
        "\n".join(
            [
                '_templates_suffix: ".jinja"',
                "_subdirectory: template",
                "",
                "module_name:",
                "  type: str",
                "feature:",
                "  type: str",
            ]
        ),
        encoding="utf-8",
    )
    (template_dir / "{{ module_name }}.txt.jinja").write_text(
        "{{ module_name }}:{{ feature }}",
        encoding="utf-8",
    )

    output_root = tmp_path / "generated"

    generate_module(
        "billing",
        output_root,
        template_root,
        data={"feature": "invoices"},
    )

    assert (output_root / "billing.txt").read_text(encoding="utf-8") == (
        "billing:invoices"
    )


def test_generate_module_raises_for_missing_template(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError, match="Copier template does not exist"):
        generate_module("billing", tmp_path / "generated", tmp_path / "missing")


def test_generate_module_uses_bundled_scaffolding(tmp_path: Path) -> None:
    output_root = tmp_path / "generated"

    generate_module("billing", output_root)

    assert (output_root / "billing" / "domain.py").is_file()
    assert (output_root / "billing" / "application.py").is_file()
