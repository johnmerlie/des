from abc import ABC
from typing import Any, ClassVar

from pydes.core import Input, Output


class Channel(ABC):
    name: str

    def __set_name__(self, owner: type, name: str):
        self.name = name

    def __get__(self, obj: object, objtype: type | None = None):
        if obj is None:
            return self
        return getattr(obj, self.name)

    def __set__(self, obj: object, value: Any):
        setattr(obj, self.name, value)


class InputChannel(Channel):
    direction: ClassVar[bool] = True

    def get(self, inputs: Input):
        return inputs[self.name]


class OutputChannel(Channel):
    direction: ClassVar[bool] = False

    def put(self, value: Any) -> Output:
        return {self.name: value}
