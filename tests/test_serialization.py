import pickle
import uuid

from pydes.message import Message


def test_initialization():
    destination = uuid.UUID("4c3e1a48-3eaf-4012-a480-be1d542028f6")
    timestamp = 1699505064221500572
    data = "some-message"

    msg = Message(destination=destination, timestamp=timestamp, content=data)
    msg.destination
    assert msg.destination == destination
    assert msg.timestamp == timestamp

    serialized = pickle.dumps(msg)

    deserialized = pickle.loads(serialized)

    assert deserialized == msg
