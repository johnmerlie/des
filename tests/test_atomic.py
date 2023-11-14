from pydes.atomic import Atomic


def test_initialization():
    model = Atomic(initial_state=4)

    assert model.name == f"{model.__class__.__name__}-{model.id}"
    assert model.state == 4
