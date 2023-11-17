import pickle
from abc import ABC
from collections.abc import Mapping
from functools import cached_property
from math import inf
from typing import Annotated, Any, ClassVar, Protocol, Self
from uuid import UUID

from annotated_types import Ge
from numpy.random import PCG64DXSM, Generator
from pydantic import BaseModel, ConfigDict, Field

__all__ = "Mutable", "Immutable", "Field", "random", "model_id", "INFINITY"

SEED = 12345

random = Generator(PCG64DXSM(SEED))


INFINITY = inf


def model_id():
    return UUID(bytes=random.bytes(16))


def model_serialize(model: Any) -> bytes:
    return pickle.dumps(model)


def model_deserialize(data: bytes) -> Any:
    return pickle.loads(data)


class HasID(Protocol):
    id: UUID


class Channel(ABC):
    direction: ClassVar[bool]
    name: str
    """
    Parameters
    ----------
    direction : bool
        True for input, False for output
    """

    def __set_name__(self, objtype: type, name: str):
        self.name = name

    @cached_property
    def is_input(self):
        return self.direction is True

    @cached_property
    def is_output(self):
        return self.direction is False


class InputChannel(Channel):
    direction: ClassVar[bool] = True
    target: UUID
    sources: set[UUID]

    def __get__(self, obj: HasID | None, objtype: type | None = None) -> Self:
        if obj is not None:
            self.target = obj.id

        return self

    def __lshift__(self, other: Any):
        if not isinstance(other, OutputChannel):
            raise TypeError(f"invalid type for comparison: type({other})={type(other)}")

        self.sources.add(source := other.source)
        other.targets.add(target := self.target)

        return source, target

    def __getitem__(self, key: UUID):
        if key not in self.sources:
            raise KeyError(f"key: {key} does not exist in sources")


class OutputChannel(Channel):
    direction: ClassVar[bool] = False
    source: UUID
    targets: set[UUID]

    def __get__(self, obj: HasID | None, objtype: type | None = None) -> Self:
        if obj is not None:
            self.source = obj.id

        return self

    def __rshift__(self, other: Any):
        if not isinstance(other, InputChannel):
            raise TypeError(f"invalid type for comparison: type({other})={type(other)}")

        other.sources.add(source := self.source)
        self.targets.add(target := other.target)

        return source, target

    # def __getitem__(self, key: UUID):
    #     if key not in self.targets:
    #         raise KeyError(f"key: {key} does not exist in targets")


# class MultiChannel(ABC):
#     count: int
#     _value: tuple[Channel, ...]

#     def __init__(self, count: int):
#         self.count = count

#     def __set_name__(self, owner: type, name: str):
#         self._value = tuple(Channel(f"{name}[{i}]") for i in range(self.count))

#     def __get__(self, obj: object | None, objtype: type | None = None):
#         if obj is None:
#             return self
#         return self._value

#     def __getitem__(self, key: int):
#         return self._value[key]


# class SingleChannelInput(SingleChannel):
#     direction: ClassVar[bool] = True


# class MultiChannelInput(MultiChannel):
#     direction: ClassVar[bool] = True


# class SingleChannelOutput(SingleChannel):
#     direction: ClassVar[bool] = False


# class MultiChannelOutput(MultiChannel):
#     direction: ClassVar[bool] = False


class Serializiable(BaseModel, ABC):
    model_config = ConfigDict(
        extra="forbid",
        ignored_types=(
            InputChannel,
            OutputChannel,
        ),
    )
    id: UUID = Field(default_factory=model_id, frozen=True, kw_only=True)

    def model_serialize(self):
        return model_serialize(self)

    @classmethod
    def model_deserialize(cls, data: bytes) -> Self:
        return pickle.loads(data)


class Mutable(Serializiable):
    model_config = ConfigDict(
        validate_assignment=True,
    )


class Immutable(Serializiable):
    model_config = ConfigDict(
        frozen=True,
    )


type Time = Annotated[float, Ge(0)]

type Input[V] = Mapping[InputChannel, V]
type Output[V] = Mapping[OutputChannel, V]
