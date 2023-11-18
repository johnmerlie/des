from __future__ import annotations

from abc import ABC
from collections.abc import Mapping
from typing import Any
from uuid import UUID
from weakref import WeakValueDictionary

from pydantic.dataclasses import dataclass
from typing_extensions import ClassVar, Self

from pydes.model import Model

__all__ = (
    "InputChannel",
    "OutputChannel",
    "Inputs",
    "Outputs",
)


@dataclass(frozen=True)
class Port:
    output: OutputChannelDescriptor
    input: InputChannelDescriptor


class ChannelDescriptor(ABC):
    direction: ClassVar[bool]
    name: str
    owner: Model

    def __set_name__(self, objtype: type[Model], name: str):
        self.name = name

    def __get__(self, obj: Model | None, objtype: type[Model] | None = None) -> Any:
        if obj is not None:
            self.owner = obj

    def _connect(self, other: Any) -> Port:
        match self, other:
            case InputChannelDescriptor(), OutputChannelDescriptor():
                port = Port(other, self)
            case OutputChannelDescriptor(), InputChannelDescriptor():
                port = Port(self, other)
            case _:
                raise ValueError(f"Invalid object pair for linking: {self} <> {other}")
        return port


class InputChannelDescriptor(ChannelDescriptor):
    direction: ClassVar[bool] = True


class OutputChannelDescriptor(ChannelDescriptor):
    direction: ClassVar[bool] = False


class SinglePortChannelDescriptor(ChannelDescriptor):
    port: Port

    def __get__(self, obj: Model | None, objtype: type[Model] | None = None) -> Port:
        super().__get__(obj, objtype)
        return self.port

    def connect(self, other: Any):
        match other:
            case SinglePortChannelDescriptor():
                self.port = other.port = self._connect(other)
            case MultiPortChannelDescriptor():
                self.port = other.ports[self.owner.id] = self._connect(other)
            case _:
                raise ValueError(f"Invalid object pair for linking: {self} <> {other}")


class MultiPortChannelDescriptor(ChannelDescriptor):
    ports: WeakValueDictionary[UUID, Port]

    def __get__(self, obj: Model | None, objtype: type[Model] | None = None) -> Self:
        super().__get__(obj, objtype)
        return self

    def __getitem__(self, key: UUID | Model) -> Port:
        if isinstance(key, Model):
            key = key.id
        return self.ports[key]

    def connect(self, other: Any):
        match other:
            case SinglePortChannelDescriptor():
                self.ports[other.owner.id] = other.port = self._connect(other)
            case MultiPortChannelDescriptor():
                self.ports[other.owner.id] = other.ports[self.owner.id] = self._connect(
                    other
                )
            case _:
                raise ValueError(f"Invalid object pair for linking: {self} <> {other}")


class InputChannel(SinglePortChannelDescriptor, InputChannelDescriptor):
    ...


class MultiInputChannel(MultiPortChannelDescriptor, InputChannelDescriptor):
    ...


class OutputChannel(SinglePortChannelDescriptor, OutputChannelDescriptor):
    ...


class MultiOutputChannel(MultiPortChannelDescriptor, OutputChannelDescriptor):
    ...


type Inputs[V] = Mapping[Port, V]
type Outputs[V] = Mapping[Port, V]
