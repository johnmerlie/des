from typing import Literal

import pytest
from pydantic.dataclasses import dataclass

from pydes.atomic import Atomic, StateConstant, StateVariable
from pydes.channel import InputChannel, Inputs, MultiOutputChannel, OutputChannel
from pydes.core import INFINITY, Time, random
from pydes.errors import InvalidInputError, InvalidStateError

# @pytest.fixture
# def monorail_model():
#     @dataclass
#     class StationState:
#         status: Literal["Empty", "Loading", "Sending", "Waiting", "Collided"]
#         vehicle: int
#         next_station_occupied: bool


@pytest.fixture
def trafficlight_model():
    type TrafficLightStatus = Literal["red", "yellow", "green", "manual"]

    class TrafficLight(Atomic):
        status: TrafficLightStatus = StateVariable("red")
        interrupt = InputChannel()
        observed = OutputChannel()

        def time_advance(self):
            match self.status:
                case "red":
                    return 60.0
                case "yellow":
                    return 10.0
                case "green":
                    return 50.0
                case "manual":
                    return INFINITY

        def external_transition(self, inputs: Inputs[str]):
            match inputs[self.interrupt]:
                case "toManual":
                    self.status = "manual"
                case "toAutomatic":
                    if self.status == "manual":
                        self.status = "red"
                case other:
                    raise InvalidInputError(other)

        def internal_transition(self):
            match self.status:
                case "red":
                    self.status = "green"
                case "green":
                    self.status = "yellow"
                case "yellow":
                    self.status = "red"
                case other:
                    raise InvalidStateError(other)

        def output(self):
            match self.status:
                case "red":
                    return {self.observed: "grey"}
                case "green":
                    return {self.observed: "yellow"}
                case "yellow":
                    return {self.observed: "grey"}
                case other:
                    raise InvalidStateError(other)

    type PolicemanStatus = Literal["idle", "working"]

    class Policeman(Atomic):
        status: PolicemanStatus = StateVariable("idle")
        interrupt = OutputChannel()

        def time_advance(self):
            """
            Time-Advance Function.
            """
            match self.status:
                case "idle":
                    return 200
                case "working":
                    return 100

        def internal_transition(self):
            """
            Internal Transition Function.
            The policeman works forever, so only one mode.
            """

            match self.status:
                case "idle":
                    self.status = "working"
                case "working":
                    self.status = "idle"

        def output(self):
            """
            Output Function.
            """
            match self.status:
                case "idle":
                    return {self.interrupt: "toManual"}
                case "working":
                    return {self.interrupt: "toAutomatic"}

    TrafficLight()
    Policeman()


@pytest.fixture
def queueing_model():
    @dataclass
    class Job:
        size: int

    class Generator(Atomic):
        remaining: int = StateVariable()
        size_param: float = StateConstant()
        generate = OutputChannel()

        def time_advance(self) -> Time:
            if self.remaining == 0:
                return INFINITY
            else:
                return random.random()

        def internal_transition(self):
            self.remaining -= 1

        def output(self):
            size = max(1, int(random.normal(self.size_param, 5)))
            return {self.generate: Job(size)}

    class Processor(Atomic):
        event: Job | None = StateVariable(None)
        speed: float = StateConstant()
        receive = InputChannel()
        send = OutputChannel()
        finish = OutputChannel()

        def time_advance(self):
            if self.event is not None:
                return 20.0 + max(1.0, self.event.size)
            else:
                return INFINITY

        def internal_transition(self):
            self.event = None

        def external_transition(self, inputs: Inputs[Job]):
            self.event = inputs[self.receive]

        def output(self):
            return {self.send: self.event, self.finish: self.id}

    class Collector(Atomic):
        events: list[Job] = StateVariable(default_factory=list)
        collect = InputChannel()

        def external_transition(self, inputs: Inputs[Job]):
            self.events.append(inputs[self.collect])

    class Queue(Atomic):
        queued_jobs: list[Job] = StateVariable(default_factory=list)
        active_job: Job | None = StateVariable(default=None)
        idle_processors: list[Processor] = StateVariable(default_factory=list)

        processing_time: float = StateConstant(1.0)

        enqueue = InputChannel()
        finish = InputChannel()
        outputs = MultiOutputChannel()

        def time_advance(self) -> Time:
            if self.queued_jobs and self.idle_processors:
                return self.processing_time
            else:
                return INFINITY

        def internal_transition(self):
            if self.queued_jobs and self.idle_processors:
                self.active_job = self.queued_jobs.pop(0)
            else:
                self.active_job = None

        def external_transition(self, inputs: Inputs[Processor | Job]):
            match inputs:
                case {self.finish: Processor() as processor}:
                    self.idle_processors.append(processor)
                    if not self.active_job and self.queued_jobs:
                        # Process first task in queue
                        self.active_job = self.queued_jobs.pop(0)
                case {self.enqueue: Job() as job}:
                    # Processing an incoming event
                    if self.idle_processors and not self.active_job:
                        # Process when idle processors
                        self.active_job = job
                    else:
                        # No idle processors, so queue it
                        self.queued_jobs.append(job)
                case _:
                    raise InvalidInputError(inputs)

        def output(self):
            return {self.outputs[self.idle_processors.pop(0)]: self.active_job}

        # def outputFnc(self):
        #     # Output the event to the processor
        #     port = self.out_proc[self.state.idle_procs[0]]
        #     return {port: self.state.processing}

    Generator()
    Processor()
    Collector()
    Queue()
