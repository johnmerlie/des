from __future__ import annotations

from abc import ABC
from uuid import UUID

from pydantic import ConfigDict, Field, model_validator

from pydes.channel import InputChannel, OutputChannel
from pydes.core import Mutable, model_id
from pydes.utils import SimulationTime


class Model(Mutable, ABC):
    model_config = ConfigDict(ignored_types=(InputChannel, OutputChannel))

    id: UUID = Field(default_factory=model_id, frozen=True)
    time: SimulationTime = Field(default_factory=SimulationTime, frozen=True)
    name: str = Field(
        default=None,
        frozen=True,
        description="The Model name used for labelling, set automatically if not provided.",
    )
    parent: Model = Field(
        default=None,
        description="The parent model in the model heirarchy",
    )

    def __hash__(self):
        return self.id.int

    @model_validator(mode="after")
    def default_name(self):
        if not self.name:
            object.__setattr__(self, "name", f"{self.__class__.__name__}-{self.id}")
        return self

    @property
    def path(self) -> str:
        return f"{self.parent.path}.{self.name}"
