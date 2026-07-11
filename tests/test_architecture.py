from modwire.architecture import ArchitectureApplication, ArchitectureConfig


def test_standard_architecture_application_exposes_stable_report_catalog() -> None:
    catalog = ArchitectureApplication.standard(ArchitectureConfig()).reports()

    assert tuple(report.id for report in catalog.reports) == (
        "architecture.map",
        "architecture.violations.flow",
        "architecture.violations.shape",
        "architecture.insights",
    )
    assert tuple(child.id for child in catalog.reports[-1].children) == (
        "architecture.insights.clusters",
        "architecture.insights.hotspots",
        "architecture.insights.coherence",
        "architecture.insights.callables",
        "architecture.insights.exports",
    )
