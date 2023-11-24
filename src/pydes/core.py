import pickle
from math import inf
from typing import Annotated, Any
from uuid import UUID

from annotated_types import Ge
from numpy.random import PCG64DXSM, Generator
from pydantic import BaseModel, ConfigDict, Field
from typing_extensions import Self

type Time = Annotated[float, Ge(0)]


SEED = 12345
INFINITY = inf

random = Generator(PCG64DXSM(SEED))


def new_id():
    return UUID(bytes=random.bytes(16))


def serialize(model: Any) -> bytes:
    return pickle.dumps(model)


def deserialize(data: bytes) -> Any:
    return pickle.loads(data)


class Serializable(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )

    def model_serialize(self):
        return serialize(self)

    @classmethod
    def model_deserialize(cls, data: bytes) -> Self:
        return pickle.loads(data)


class Mutable(Serializable):
    model_config = ConfigDict(
        validate_assignment=True,
    )


class Immutable(Serializable):
    model_config = ConfigDict(
        frozen=True,
    )


class Base(Mutable):
    id: UUID = Field(
        default_factory=new_id,
        frozen=True,
    )
