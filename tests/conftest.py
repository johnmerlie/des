from dataclasses import field
from typing import Any, Literal

import pytest
from pydantic import Field
from pydantic.dataclasses import dataclass

from pydes.atomic import Atomic
from pydes.channel import InputChannel, OutputChannel
from pydes.core import INFINITY, Input, Time, random
from pydes.errors import InvalidInputError, InvalidStateError


@pytest.fixture
def monorail_model():
    @dataclass
    class StationState:
        status: Literal["Empty", "Loading", "Sending", "Waiting", "Collided"]
        vehicle: int
        next_station_occupied: bool


@pytest.fixture
def trafficlight_model():
    @dataclass
    class TrafficLightState:
        status: Literal["red", "yellow", "green", "manual"] = Field("red")

    class TrafficLight(Atomic[TrafficLightState]):
        interrupt = InputChannel()
        observed = OutputChannel()

        @classmethod
        def time_advance(cls, state: TrafficLightState):
            match state.status:
                case "red":
                    return 60.0
                case "yellow":
                    return 10.0
                case "green":
                    return 50.0
                case "manual":
                    return INFINITY

        @classmethod
        def external_transition(cls, state: TrafficLightState, inputs: Input):
            match cls.interrupt.get(inputs):
                case "toManual":
                    state.status = "manual"
                case "toAutomatic":
                    if state.status == "manual":
                        state.status = "red"
                case other:
                    raise InvalidInputError(other)
            return state

        @classmethod
        def internal_transition(cls, state: TrafficLightState):
            match state.status:
                case "red":
                    state.status = "green"
                case "green":
                    state.status = "yellow"
                case "yellow":
                    state.status = "red"
                case other:
                    raise InvalidStateError(other)
            return state

        @classmethod
        def output(cls, state: TrafficLightState):
            match state.status:
                case "red":
                    return cls.observed.put("grey")
                case "green":
                    return cls.observed.put("yellow")
                case "yellow":
                    return cls.observed.put("grey")
                case other:
                    raise InvalidStateError(other)

    @dataclass
    class PolicemanState:
        status: Literal["idle", "working"]

    class Policeman(Atomic[PolicemanState]):
        interrupt = OutputChannel()

        @classmethod
        def time_advance(cls, state: PolicemanState):
            """
            Time-Advance Function.
            """
            match state.status:
                case "idle":
                    return 200
                case "working":
                    return 100
            raise InvalidStateError(state)

        @classmethod
        def internal_transition(cls, state: PolicemanState):
            """
            Internal Transition Function.
            The policeman works forever, so only one mode.
            """

            match state.status:
                case "idle":
                    state.status = "working"
                case "working":
                    state.status = "idle"
            return state

        @classmethod
        def output(cls, state: PolicemanState):
            """
            Output Funtion.
            """
            match state.status:
                case "idle":
                    return cls.interrupt.put("toManual")
                case "working":
                    return cls.interrupt.put("toAutomatic")
            raise InvalidStateError(state)


@pytest.fixture
def queueing_model():
    @dataclass
    class CollectorState:
        events: list[Any] = field(default_factory=list)

    class Collector(Atomic[CollectorState]):
        collect = InputChannel()

        @classmethod
        def external_transition(cls, state: CollectorState, inputs: Input) -> CollectorState:
            state.events.append(cls.collect.get(inputs))
            return state

    @dataclass
    class GeneratorState:
        remaining: int
        size_param: float = Field(frozen=True)

    @dataclass
    class Job:
        size: int

    class Generator(Atomic[GeneratorState]):
        generate = OutputChannel()

        @classmethod
        def time_advance(cls, state: GeneratorState) -> Time:
            if state.remaining == 0:
                return INFINITY
            else:
                return random.random()

        @classmethod
        def internal_transition(cls, state: GeneratorState) -> GeneratorState:
            state.remaining -= 1
            return state

        @classmethod
        def output(cls, state: GeneratorState):
            size = max(1, int(random.normal(state.size_param, 5)))
            return cls.generate.put(Job(size))

    @dataclass
    class ProcessorState:
        event: Job | None = field(default=None)

    class Processor(Atomic[ProcessorState]):
        receive = InputChannel()
        send = OutputChannel()
        finish = OutputChannel()

        # def __init__(self, nr, proc_param):
        #     AtomicDEVS.__init__(self, "Processor_%i" % nr)

        #     self.state = ProcessorState()
        #     self.in_proc = self.addInPort("in_proc")
        #     self.out_proc = self.addOutPort("out_proc")
        #     self.out_finished = self.addOutPort("out_finished")

        #     # Define the parameters of the model
        #     self.speed = proc_param
        #     self.nr = nr

        @classmethod
        def internal_transition(cls, state: ProcessorState):
            state.event = None
            return state

        @classmethod
        def external_transition(cls, state: ProcessorState, inputs: Input):
            state.event = cls.receive.get(inputs)
            return state

        @classmethod
        def time_advance(cls, state: ProcessorState):
            if state.event is not None:
                return 20.0 + max(1.0, state.event.size)
            else:
                return INFINITY

        @classmethod
        def output(cls, state: ProcessorState):
            return cls.send.put(state.event) | cls.finish.put(state.event)

        # def outputFnc(self):
        #     # Output the processed event and signal as finished
        #     return {self.out_proc: self.state.evt, self.out_finished: self.nr}
