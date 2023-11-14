from typing import ClassVar

from pydes.atomic import Atomic, StateConstant, StateVariable
from pydes.model import InputChannel


def test_initialization():
    class TestModel(Atomic):
        number: int = StateVariable(4)
        const: int = StateConstant(5)
        input: ClassVar = InputChannel()

    model = TestModel()
