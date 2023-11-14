from pydantic import Field

from pydes.core import INFINITY, Input, Output, Time
from pydes.model import Model


class Atomic[S](Model):
    state: S = Field(alias="initial_state")

    @classmethod
    def time_advance(cls, state: S) -> Time:
        """Override this function to implement custom time advance

        Default implementation returns infinity, i.e. the model will
        never undergo internal transition.
        """
        return INFINITY

    @classmethod
    def external_transition(cls, state: S, inputs: Input) -> S:
        """Override this function to implement custom external transition

        Default Implementation returns `state` unchanged.
        """
        return state

    @classmethod
    def confluent_transition(cls, state: S, inputs: Input):
        """Override this function to implement custom confluent transition

        Default Implementation processes `internal_transition` followed by
        `external_transition`
        """
        state = cls.internal_transition(state)
        state = cls.external_transition(state, inputs)
        return state

    @classmethod
    def internal_transition(cls, state: S) -> S:
        """Override this function to implement custom internal transition

        Default Implementation returns `state` unchanged.
        """
        return state

    @classmethod
    def condition(cls, state: S) -> bool:
        """Override this function to implement custom condition function

        Default Implementation returns True
        """
        return True

    @classmethod
    def output(cls, state: S) -> Output:
        """Override this function to implement custom output function

        Default Implementation returns empty map representing no output
        """
        return {}
