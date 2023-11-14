import pickle
from abc import ABC
from collections.abc import Mapping
from math import inf
from typing import Annotated, Any, ClassVar, Self, overload
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


class Channel:
    name: str

    def __init__(self, name: str):
        self.name = name

    def __hash__(self):
        return hash(self.name)


class SingleChannel(ABC):
    _value: Channel

    def __set_name__(self, owner: type, name: str):
        self._value = Channel(name)

    @overload
    def __get__(self, obj: object, objtype: type | None = None) -> Channel:
        ...

    @overload
    def __get__(self, obj: None, objtype: type | None = None) -> Self:
        ...

    def __get__(self, obj: object | None, objtype: type | None = None):
        if obj is None:
            return self
        return self._value


class MultiChannel(ABC):
    count: int
    _value: tuple[Channel, ...]

    def __init__(self, count: int):
        self.count = count

    def __set_name__(self, owner: type, name: str):
        self._value = tuple(Channel(f"{name}[{i}]") for i in range(self.count))

    def __get__(self, obj: object | None, objtype: type | None = None):
        if obj is None:
            return self
        return self._value

    def __getitem__(self, key: int):
        return self._value[key]


class SingleChannelInput(SingleChannel):
    direction: ClassVar[bool] = True


class MultiChannelInput(MultiChannel):
    direction: ClassVar[bool] = True


class SingleChannelOutput(SingleChannel):
    direction: ClassVar[bool] = False


class MultiChannelOutput(MultiChannel):
    direction: ClassVar[bool] = False


class Serializiable(BaseModel, ABC):
    model_config = ConfigDict(
        extra="forbid",
        ignored_types=(
            SingleChannelInput,
            MultiChannelInput,
            SingleChannelOutput,
            MultiChannelOutput,
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

type Input[V] = Mapping[Channel, V]
type Output[V] = Mapping[Channel, V]
