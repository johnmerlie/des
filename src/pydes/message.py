from typing import Any
from uuid import UUID

from .core import Immutable


class Message(Immutable):
    destination: UUID
    timestamp: int
    content: Any
