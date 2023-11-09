import uuid

from pydes.message import Message
from pydes.utils import deserialize, serialize


def test_initialization():
    destination = uuid.UUID("4c3e1a48-3eaf-4012-a480-be1d542028f6")
    timestamp = 1699505064221500572
    data = "some-message"

    msg = Message(destination, timestamp, data)
    msg.destination
    assert msg.destination == destination
    assert msg.timestamp == timestamp

    serialized = serialize(msg)

    assert (
        serialized
        == b"\xc7Y\x02\x84\xa2id\xd8\x01<\xf1\xa6\xe6\x9c.\x18\x07\xcd\xce\xd3\x95\xad~\x1d\xe8\xabdestination\xd8\x01L>\x1aH>\xaf@\x12\xa4\x80\xbe\x1dT (\xf6\xa9timestamp\xcf\x17\x95\xda\xd9\xfe\xe6d\x9c\xa4data\xacsome-message"
    )

    deserialized = deserialize(serialized)

    assert deserialized == msg
