from dataclasses import dataclass, field
from uuid import UUID

from .utils import Serializable, new_uuid


@dataclass(
    frozen=True,
    slots=True,
)
class Message(Serializable):
    id: UUID = field(kw_only=True, default_factory=new_uuid)
    destination: UUID
    timestamp: int
    data: str
