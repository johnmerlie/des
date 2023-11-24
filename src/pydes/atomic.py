from typing import Any, Callable

from pydantic import Field
from pydantic_core import PydanticUndefined

from pydes.channel import Inputs, Outputs
from pydes.core import INFINITY, Time
from pydes.model import Model

__all__ = (
    "StateVariable",
    "StateConstant",
    "Atomic",
)

Unset: Any = PydanticUndefined


def StateVariable(
    default: Any = Unset,
    default_factory: Callable[[], Any] | None = Unset,
):
    return Field(
        default=default,
        default_factory=default_factory,
        frozen=False,
    )


def StateConstant(
    default: Any = Unset,
    default_factory: Callable[[], Any] | None = Unset,
):
    return Field(
        default=default,
        default_factory=default_factory,
        frozen=True,
    )


class Atomic(Model):
    def time_advance(self) -> Time:
        """Override this function to implement custom time advance

        Default implementation returns infinity, i.e. the model will
        never undergo internal transition.
        """
        return INFINITY

    def external_transition(self, inputs: Inputs[Any]) -> None:
        """Override this function to implement custom external transition

        Default Implementation returns `state` unchanged.
        """
        pass

    def confluent_transition(self, inputs: Inputs[Any]):
        """Override this function to implement custom confluent transition

        Default Implementation processes `internal_transition` followed by
        `external_transition`
        """
        self.internal_transition()
        self.external_transition(inputs)

    def internal_transition(self):
        """Override this function to implement custom internal transition

        Default Implementation returns `state` unchanged.
        """
        pass

    def condition(self) -> bool:
        """Override this function to implement custom condition function

        Default Implementation returns True
        """
        return True

    def output(self) -> Outputs[Any]:
        """Override this function to implement custom output function

        Default Implementation returns empty map representing no output
        """
        return {}
