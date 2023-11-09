from abc import ABC
from dataclasses import Field, fields
from enum import IntEnum, auto
from typing import ClassVar, Self, overload
from uuid import UUID
from weakref import WeakKeyDictionary, WeakValueDictionary

import msgpack as mp
from numpy.random import default_rng

type ScalarPackable = None | bool | int | bytes | bytearray | str | memoryview | float
type StructuralPackable[T] = list[T] | tuple[T, ...] | dict[str, T]
type DefaultPackable = ScalarPackable | StructuralPackable[Packable]
type CustomPackable = UUID
type Packable = DefaultPackable | CustomPackable | Serializable


random = default_rng(123456789)


def new_uuid():
    return UUID(bytes=random.bytes(16))


class Tag(IntEnum):
    UUID = auto()


class Serializable(ABC):
    __dataclass_fields__: dict[str, Field[Packable]]
    __tags: ClassVar[WeakKeyDictionary[type[Self], int]] = WeakKeyDictionary()
    __registry: ClassVar[WeakValueDictionary[int, type[Self]]] = WeakValueDictionary()

    def __init_subclass__(cls) -> None:
        super().__init_subclass__()
        _tag = len(Tag) + len(Serializable.__registry)
        Serializable.__tags[cls], Serializable.__registry[_tag] = _tag, cls

    @staticmethod
    def check_tag(tag: int):
        return tag in Serializable.__registry

    @staticmethod
    def get_tag(subcls: type):
        return Serializable.__tags[subcls]

    @staticmethod
    def get_subcls(tag: int):
        return Serializable.__registry[tag]


def _as_dict(obj: Serializable) -> dict[str, Packable]:
    return dict((fld.name, getattr(obj, fld.name)) for fld in fields(obj))


@overload
def serializer(obj: CustomPackable) -> mp.ExtType:
    ...


@overload
def serializer(obj: Serializable) -> mp.ExtType:
    ...


@overload
def serializer(obj: DefaultPackable) -> bytes:
    ...


def serializer(obj: Packable) -> bytes | mp.ExtType:
    match obj:
        case Serializable():
            return mp.ExtType(
                Serializable.get_tag(type(obj)),
                serialize(_as_dict(obj)),
            )
        case UUID():
            return mp.ExtType(Tag.UUID, obj.bytes)
        case _:
            raise TypeError(obj)


def serialize(obj: Packable) -> bytes:
    return mp.packb(obj, default=serializer)


def deserializer(tag: int, msg: bytes) -> CustomPackable | Serializable:
    match tag:
        case Tag.UUID:
            return UUID(bytes=msg)
        case key if Serializable.check_tag(key):
            subcls = Serializable.get_subcls(tag)
            return subcls(**deserialize(msg))
        case _:
            raise TypeError((tag, msg))


def deserialize(msg: bytes) -> Packable:
    return mp.unpackb(msg, ext_hook=deserializer)  # type: ignore
