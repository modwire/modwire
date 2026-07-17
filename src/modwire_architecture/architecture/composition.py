from modwire_architecture.shared import config

from .boundaries import standard_flow_report_collector
from .insights import standard_insight_report_collector
from .map import standard_map_components
from .shape import standard_shape_report_collector


def standard_architecture_components(
    config_: config.ArchitectureConfig,
):
    map_loader, map_collector = standard_map_components(config_)
    return (
        map_loader,
        (
            map_collector,
            standard_flow_report_collector(config_),
            standard_insight_report_collector(),
            standard_shape_report_collector(config_),
        ),
    )
