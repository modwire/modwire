from modwire.shared import ModwireBaseModel


class ShapeViolation(ModwireBaseModel):
    source_id: str
    rule_name: str
    actual: int | str | bool
    limit: int | str | bool
    symbol_kind: str = ""
    symbol_name: str = ""


class ShapeReport(ModwireBaseModel):
    violations: tuple[ShapeViolation, ...] = ()
    resolvers: tuple[str, ...] = ()
