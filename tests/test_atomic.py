from pydes.atomic import Atomic, StateConstant, StateVariable
from pydes.core import SingleChannelInput


def test_initialization():
    class TestModel(Atomic):
        number: int = StateVariable(4)
        const: int = StateConstant(5)
        input = SingleChannelInput()

    model = TestModel()
