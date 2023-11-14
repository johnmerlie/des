from pydes.utils import MapQueue


def test_queue():
    q = MapQueue[str]([(665, "red"), (470, "blue"), (550, "green")])

    assert q.position["blue"] == 0

    q.remove("red")
    q.update("green", "violet", 400)
    assert q.push("indigo", 425)

    queued = [q.pop() for _ in range(len(q))]
    assert queued == ["violet", "indigo", "blue"]
