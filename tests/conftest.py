from typing import Literal

import pytest
from pydantic.dataclasses import dataclass


@pytest.fixture
def monorail_model():
    @dataclass
    class StationState:
        status: Literal["Empty", "Loading", "Sending", "Waiting", "Collided"]
        vehicle: int
        next_station_occupied: bool
