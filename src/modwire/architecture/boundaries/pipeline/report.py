from modwire.shared import ModwireBaseModel

from ..base import FlowViolation
from ..config import FlowRealm, FlowRules


class FlowReport(ModwireBaseModel):
    violations: tuple[FlowViolation, ...] = ()
    analyzers: tuple[str, ...] = ()


class FlowRealmSelector:
    def select(self, flow: FlowRules) -> tuple[FlowRealm, ...]:
        if flow.realms:
            return tuple(
                FlowRealm(
                    name=realm.name,
                    module_tag=realm.module_tag or flow.module_tag,
                    layers=realm.layers or flow.layers,
                )
                for realm in flow.realms
            )
        return (
            FlowRealm(
                module_tag=flow.module_tag,
                layers=flow.layers,
            ),
        )