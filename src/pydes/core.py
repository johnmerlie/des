import pickle
from abc import ABC
from collections.abc import Mapping
from math import inf
from typing import Annotated, Any, Self
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


class Serializiable(BaseModel, ABC):
    id: UUID = Field(default_factory=model_id, frozen=True, kw_only=True)

    def model_serialize(self):
        return model_serialize(self)

    @classmethod
    def model_deserialize(cls, data: bytes) -> Self:
        return pickle.loads(data)


class Mutable(Serializiable):
    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
    )


class Immutable(Serializiable):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )


type Time = Annotated[float, Ge(0)]

type Input = Mapping[str, Any]
type Output = Mapping[str, Any]
