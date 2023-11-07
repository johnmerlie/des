from dataclasses import dataclass, field
from uuid import UUID, uuid4

import ormsgpack as mp


def to_uuid(obj: UUID | str):
    match obj:
        case UUID():
            return obj
        case _:
            return UUID(obj)


@dataclass(frozen=True, slots=True)
class Message:
    id: UUID = field(init=False, default_factory=uuid4)
    destination: UUID
    timestamp: int
    data: str

    def serialize(self):
        return mp.packb(self)

    @classmethod
    def deserialize(cls, msg: bytes):
        return cls(**mp.unpackb(msg))
