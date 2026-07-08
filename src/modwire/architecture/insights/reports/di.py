from dependency_injector import containers, providers

from .report import InsightReportCollector, InsightReporterCatalog


class InsightsReportsContainer(containers.DeclarativeContainer):
    catalog = providers.Singleton(InsightReporterCatalog)

    report = providers.Factory(
        InsightReportCollector,
        catalog=catalog,
    )
