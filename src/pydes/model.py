from abc import ABC
from typing import ClassVar, Self, overload

from pydantic import model_validator

from pydes.core import Field, Mutable
from pydes.utils import SimulationTime


class Channel(ABC):
    name: str

    def __set_name__(self, owner: type, name: str):
        self.name = name

    @overload
    def __get__(self, obj: object, objtype: type | None = None) -> str:
        ...

    @overload
    def __get__(self, obj: None, objtype: type | None = None) -> Self:
        ...

    def __get__(self, obj: object | None, objtype: type | None = None):
        if obj is None:
            return self
        return self.name


class InputChannel(Channel):
    direction: ClassVar[bool] = True


class OutputChannel(Channel):
    direction: ClassVar[bool] = False


class Model(Mutable, ABC):
    time: SimulationTime = Field(default_factory=SimulationTime, frozen=True)
    name: str = Field(
        default=None,
        frozen=True,
        description="The Model name used for labelling, set automatically if not provided.",
    )
    parent: "Model" = Field(
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
