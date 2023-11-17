import pickle
from abc import ABC
from collections.abc import Mapping
from functools import cached_property
from math import inf
from typing import Annotated, Any, NoReturn
from uuid import UUID
from weakref import WeakValueDictionary

from annotated_types import Ge
from numpy.random import PCG64DXSM, Generator
from pydantic import BaseModel, ConfigDict, Field
from typing_extensions import ClassVar, Literal, Protocol, Self, final, overload

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


type ChType = Channel


class Channel(ABC):
    direction: ClassVar[bool]
    name: str
    owner: HasID
    links: WeakValueDictionary[UUID, HasID]
    """
    Parameters
    ----------
    direction : bool
        True for input, False for output
    """

    def __set_name__(self, objtype: type, name: str):
        self.name = name

    def __get__(self, obj: HasID | None, objtype: type | None = None) -> Self:
        if obj is not None:
            self.owner = obj

        return self

    @cached_property
    def oid(self):
        return self.owner.id

    @cached_property
    def is_input(self):
        return self.direction is True

    @cached_property
    def is_output(self):
        return self.direction is False

    def _connect(self, other: ChType):
        self.links[other.owner.id], other.links[self.owner.id] = other.owner, self.owner

    def connect(self, other: ChType):
        match self, other:
            case (InputChannel(), OutputChannel()) | (InputChannel(), OutputChannel()):
                return self._connect(other)
            case _:
                raise ValueError(f"Invalid object pair for linking: {self} <> {other}")

    def __lshift__(self, other: ChType):
        match self, other:
            case InputChannel(), OutputChannel():
                self.connect(other)
                return other.oid, self.oid
            case _:
                raise ValueError(f"Invalid object pair for linking: {self} << {other}")

    def __rshift__(self, other: ChType):
        match self, other:
            case OutputChannel(), InputChannel():
                self.connect(other)
                return self.oid, other.oid
            case _:
                raise ValueError(f"Invalid object pair for linking: {self} >> {other}")


@final
class InputChannel(Channel):
    direction = True
    # def __getitem__(self, key: UUID):
    #     if key not in self.sources:
    #         raise KeyError(f"key: {key} does not exist in sources")


@final
class OutputChannel(Channel):
    direction = False


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
