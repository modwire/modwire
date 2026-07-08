from dependency_injector import containers, providers

from .reports import InsightsReportsContainer


class InsightsContainer(containers.DeclarativeContainer):
    reports = providers.Container(InsightsReportsContainer)
