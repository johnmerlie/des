from abc import ABC
from collections.abc import Set
from typing import Any

from .model import Model


class Coupled(ABC):
    components: Set[Model[Any, Any, Any]]

    def __init__(self, components: Set[Model[Any, Any, Any]]):
        self.components = components
