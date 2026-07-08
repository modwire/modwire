from pathlib import Path

from tests.functional.cli_helpers import run_cli
from tests.functional.glossary.helpers import read_glossary


def add_term(
    cwd: Path,
    term: str,
    definition: str = "A clear glossary definition.",
    *extra_args: str,
):
    return run_cli(
        ["glossary", "add-term", term, "-d", definition, *extra_args],
        cwd,
    )


def test_adds_root_term(tmp_path: Path):
    result = add_term(
        tmp_path,
        "Modwire",
        "A tool for mapping software architecture boundaries.",
    )

    assert result.exit_code == 0
    assert "Added glossary term: modwire" in result.output

    glossary = read_glossary(tmp_path)
    assert glossary["terms"] == [
        {
            "id": "modwire",
            "parent_id": "modwire",
            "term": "Modwire",
            "definition": "A tool for mapping software architecture boundaries.",
            "aliases": [],
            "relations": [],
            "sources": [],
        }
    ]


def test_adds_child_term(tmp_path: Path):
    assert add_term(tmp_path, "Architecture").exit_code == 0

    result = add_term(
        tmp_path,
        "Layer",
        "A grouping inside an architecture.",
        "--parent-id",
        "architecture",
    )

    assert result.exit_code == 0
    assert "Added glossary term: architecture.layer" in result.output

    child = read_glossary(tmp_path)["terms"][1]
    assert child["id"] == "layer"
    assert child["parent_id"] == "architecture"


def test_rejects_unknown_parent(tmp_path: Path):
    result = add_term(
        tmp_path,
        "Layer",
        "A grouping inside an architecture.",
        "--parent-id",
        "missing",
    )

    assert result.exit_code != 0
    assert "Glossary parent does not exist: missing" in result.output


def test_rejects_duplicate_term(tmp_path: Path):
    assert add_term(tmp_path, "Modwire").exit_code == 0

    result = add_term(tmp_path, "Modwire")

    assert result.exit_code != 0
    assert "Glossary term already exists: modwire" in result.output


def test_rejects_invalid_relation(tmp_path: Path):
    result = add_term(
        tmp_path,
        "Module",
        "A deployable or design-level code grouping.",
        "--relation",
        "missing",
    )

    assert result.exit_code != 0
    assert "Glossary relation does not exist: missing" in result.output


def test_rejects_removing_parent_with_child(tmp_path: Path):
    assert add_term(tmp_path, "Architecture").exit_code == 0
    assert add_term(
        tmp_path,
        "Layer",
        "A grouping inside an architecture.",
        "--parent-id",
        "architecture",
    ).exit_code == 0

    result = run_cli(["glossary", "remove-term", "architecture"], tmp_path)

    assert result.exit_code != 0
    assert (
        "Glossary term has child terms and cannot be removed: architecture"
        in result.output
    )


def test_rejects_removing_referenced_term(tmp_path: Path):
    assert add_term(tmp_path, "Domain").exit_code == 0
    assert add_term(
        tmp_path,
        "Module",
        "A deployable or design-level code grouping.",
        "--relation",
        "domain",
    ).exit_code == 0

    result = run_cli(["glossary", "remove-term", "domain"], tmp_path)

    assert result.exit_code != 0
    assert (
        "Glossary term is referenced by another term and cannot be removed: domain"
        in result.output
    )


def test_updates_and_clears_list_data(tmp_path: Path):
    assert (
        add_term(
            tmp_path,
            "Modwire",
            "A tool for mapping software architecture.",
            "--alias",
            "modwire",
        ).exit_code
        == 0
    )

    assert run_cli(
        ["glossary", "update-term-data", "modwire", "aliases", "modwire"],
        tmp_path,
    ).exit_code == 0
    assert run_cli(
        ["glossary", "update-term-data", "modwire", "aliases", "mw"],
        tmp_path,
    ).exit_code == 0

    glossary = read_glossary(tmp_path)
    assert glossary["terms"][0]["aliases"] == ["modwire", "mw"]

    result = run_cli(
        ["glossary", "remove-term-data", "modwire", "aliases"],
        tmp_path,
    )

    assert result.exit_code == 0
    assert read_glossary(tmp_path)["terms"][0]["aliases"] == []
