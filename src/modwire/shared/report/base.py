from typing import Any, Generic, Protocol, TypeVar

from pydantic import Field, model_serializer

from modwire.shared import ModwireBaseModel


ReportResult = TypeVar("ReportResult", bound="ReportNode", covariant=True)


class ReportCollector(Protocol, Generic[ReportResult]):
    report_type: type[ReportResult]

    def collect(self, architecture_map: object) -> ReportResult:
        ...


class ReportMetadata(ModwireBaseModel):
    id: str
    title: str
    description: str
    model: str
    path: str
    order: int
    children: tuple["ReportMetadata", ...] = ()


class ReportCatalog(ModwireBaseModel):
    reports: tuple[ReportMetadata, ...]


class ReportNode(ModwireBaseModel):
    report_id: str
    report_title: str
    report_description: str = ""
    report_path: str = ""
    report_order: int = 100
    report_children: tuple[type["ReportNode"], ...] = Field(default=(), exclude=True)

    metadata: ReportMetadata = ReportMetadata(
        id="",
        title="",
        description="",
        model="",
        path="",
        order=100,
    )

    def model_post_init(self, __context: object) -> None:
        object.__setattr__(self, "metadata", self.report_metadata())

    @model_serializer(mode="wrap")
    def serialize_report_node(self, handler: Any) -> dict[str, Any]:
        payload = handler(self)
        for field_name in (
            "report_id",
            "report_title",
            "report_description",
            "report_path",
            "report_order",
            "report_children",
        ):
            payload.pop(field_name, None)
        return payload

    @classmethod
    def report_slug(cls) -> str:
        return cls.report_field("report_id").rsplit(".", 1)[-1]

    @classmethod
    def report_metadata(cls) -> ReportMetadata:
        report_children = cls.report_field("report_children")
        children = tuple(
            child.report_metadata()
            for child in sorted(
                report_children,
                key=lambda child: (
                    child.report_field("report_order"),
                    child.report_field("report_id"),
                ),
            )
        )
        report_id = cls.report_field("report_id")
        report_path = cls.report_field("report_path")
        return ReportMetadata(
            id=report_id,
            title=cls.report_field("report_title"),
            description=cls.report_field("report_description"),
            model=f"{cls.__module__}.{cls.__qualname__}",
            path=report_path or report_id,
            order=cls.report_field("report_order"),
            children=children,
        )

    @classmethod
    def report_field(cls, field_name: str) -> Any:
        return cls.model_fields[field_name].default


class ReportSection(ReportNode):
    ...


class ReportItem(ReportNode):
    ...
