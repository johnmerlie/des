from uuid import UUID

from .core import Field, Immutable
from .utils import new_uuid


class Message(Immutable):
    id: UUID = Field(default_factory=new_uuid, kw_only=True)
    destination: UUID
    timestamp: int
    data: str
