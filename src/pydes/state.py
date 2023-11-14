from typing import Any


class State:
    name: str

    def __set_name__(self, owner: type, name: str):
        self.name = name

    def __get__(self, obj: object, objtype: type | None = None):
        if obj is None:
            return self
        return getattr(obj, self.name)

    def __set__(self, obj: object, value: Any):
        setattr(obj, self.name, value)
