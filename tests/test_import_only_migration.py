from pathlib import Path


FIXTURE_DIRECTORY = Path(__file__).parent / "fixtures" / "import_only"


def test_consumer_migration_changes_only_the_import_namespace() -> None:
    before = (FIXTURE_DIRECTORY / "consumer_before.py").read_text()
    after = (FIXTURE_DIRECTORY / "consumer_after.py").read_text()

    assert after == before.replace(
        "from modwire import",
        "from modwire_architecture import",
    )


def test_renamed_consumer_uses_the_existing_public_api() -> None:
    namespace: dict[str, object] = {}
    source = (FIXTURE_DIRECTORY / "consumer_after.py").read_text()

    exec(compile(source, "consumer_after.py", "exec"), namespace)

    catalog = namespace["catalog"]()

    assert tuple(report.id for report in catalog.reports) == (
        "architecture.map",
        "architecture.violations.flow",
        "architecture.violations.shape",
        "architecture.insights",
    )
