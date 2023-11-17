from uuid import UUID

import pytest

from pydes.core import InputChannel, MultiChannel, OutputChannel


class Example:
    id: UUID

    def __init__(self, id: UUID):
        self.id = id


class Output(Example):
    ch = OutputChannel()


class Input(Example):
    ch = InputChannel()


def test_initialization():
    ids = (
        UUID("22745b8f-2949-47d2-ad5b-7f0de87f981b"),
        UUID("be272cfb-d382-4edc-9678-ecef5bdbfd0d"),
    )

    assert isinstance(Output.ch, OutputChannel)
    assert Output.ch.name == "ch"
    assert Output.ch.direction == False

    with pytest.raises(AttributeError):
        Output.ch.source

    with pytest.raises(AttributeError):
        Output.ch.targets

    assert isinstance(Input.ch, InputChannel)
    assert Input.ch.name == "ch"
    assert Input.ch.direction is True

    with pytest.raises(AttributeError):
        Input.ch.sources

    with pytest.raises(AttributeError):
        Input.ch.target

    xo = Output(ids[0])

    assert xo.id is ids[0]
    assert xo.ch.name == "ch"
    assert xo.ch.direction is False
    assert xo.ch.source is ids[0]

    with pytest.raises(AttributeError):
        xo.ch.targets

    xi = Input(ids[1])

    assert xi.id is ids[1]
    assert xi.ch.name == "ch"
    assert xi.ch.direction is True
    assert xi.ch.target is ids[1]

    with pytest.raises(AttributeError):
        xi.ch.sources


def test_right_shift():
    ids = (
        UUID("efca7392-881c-4123-97ce-231797c72c9a"),
        UUID("3639d9b6-93a2-41c6-9bb6-4971b4463732"),
    )

    xo, xi = Output(ids[0]), Input(ids[1])

    with pytest.raises(NotImplementedError):
        _ = xi.ch >> xo.ch

    s, t = xo.ch >> xi.ch

    assert (s, t) == ids
    assert s == xo.ch.source
    assert t in xo.ch.targets
    assert s in xi.ch.sources
    assert t == xi.ch.target


def test_left_shift():
    ids = (
        UUID("44a5c8a9-0fee-4d76-9a17-c5a11a9e5ba9"),
        UUID("cdf2fd2a-764a-4d9b-b8e2-7b3dab567136"),
    )

    xo, xi = Output(ids[0]), Input(ids[1])

    with pytest.raises(NotImplementedError):
        _ = xo.ch << xi.ch

    s, t = xi.ch << xo.ch

    assert (s, t) == ids
    assert s == xo.ch.source
    assert t in xo.ch.targets
    assert s in xi.ch.sources
    assert t == xi.ch.target
