from __future__ import annotations

from enum import StrEnum
from typing import ClassVar, Generic, Protocol, TypeVar

from modwire.shared import ModwireBaseModel


ReportResult = TypeVar("ReportResult", covariant=True)


class ReportCollector(Protocol, Generic[ReportResult]):
    def collect(self, architecture_map: object) -> ReportResult:
        ...


class ReportCategory(StrEnum):
    ROOT = "root"
    MAP = "map"
    VIOLATIONS = "violations"
    FLOW = "flow"
    SHAPE = "shape"
    INSIGHTS = "insights"
    INSIGHT = "insight"
    ITEM = "item"


class ReportMetadata(ModwireBaseModel):
    id: str
    title: str
    category: ReportCategory
    model: str
    path: str
    order: int
    children: tuple["ReportMetadata", ...] = ()


class ReportNode(ModwireBaseModel):
    report_id: ClassVar[str]
    report_title: ClassVar[str]
    report_category: ClassVar[ReportCategory]
    report_path: ClassVar[str] = ""
    report_order: ClassVar[int] = 100
    report_children: ClassVar[tuple[type["ReportNode"], ...]] = ()

    @classmethod
    def report_slug(cls) -> str:
        return cls.report_id.rsplit(".", 1)[-1]

    @classmethod
    def report_metadata(cls) -> ReportMetadata:
        children = tuple(
            child.report_metadata()
            for child in sorted(
                cls.report_children,
                key=lambda child: (child.report_order, child.report_id),
            )
        )
        return ReportMetadata(
            id=cls.report_id,
            title=cls.report_title,
            category=cls.report_category,
            model=f"{cls.__module__}.{cls.__qualname__}",
            path=cls.report_path or cls.report_id,
            order=cls.report_order,
            children=children,
        )


class ReportSection(ReportNode):
    ...


class ReportItem(ReportNode):
    report_category: ClassVar[ReportCategory] = ReportCategory.ITEM


__all__ = [
    "ReportCategory",
    "ReportCollector",
    "ReportItem",
    "ReportMetadata",
    "ReportNode",
    "ReportSection",
]
