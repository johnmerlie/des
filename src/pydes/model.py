from abc import ABC
from typing import Self

from pydantic import model_validator

from pydes.core import Field, Immutable
from pydes.utils import SimulationTime


class Model(Immutable, ABC):
    time: SimulationTime = Field(default_factory=SimulationTime, frozen=True)
    name: str = Field(
        default=None,
        frozen=True,
        description="The Model name used for labelling, set automatically if not provided.",
    )
    parent: Self = Field(
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
