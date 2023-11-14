from dataclasses import field
from typing import Any, Literal

import pytest
from pydantic import Field
from pydantic.dataclasses import dataclass

from pydes.atomic import Atomic, StateConstant, StateVariable
from pydes.core import INFINITY, Input, Time, random
from pydes.errors import InvalidInputError, InvalidStateError
from pydes.model import InputChannel, OutputChannel


@pytest.fixture
def monorail_model():
    @dataclass
    class StationState:
        status: Literal["Empty", "Loading", "Sending", "Waiting", "Collided"]
        vehicle: int
        next_station_occupied: bool


@pytest.fixture
def trafficlight_model():
    class TrafficLight(Atomic):
        status: Literal["red", "yellow", "green", "manual"] = StateVariable("red")
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

        def external_transition(self, inputs: Input):
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

    TrafficLight()

    class Policeman(Atomic):
        status: Literal["idle", "working"] = StateVariable("idle")
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
            Output Funtion.
            """
            match self.status:
                case "idle":
                    return {self.interrupt: "toManual"}
                case "working":
                    return {self.interrupt: "toAutomatic"}


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

        def external_transition(self, inputs: Input):
            self.event = inputs[self.receive]

        def output(self):
            return {self.send: self.event, self.finish: self.id}

    class Collector(Atomic):
        events: list[Job] = StateVariable(default_factory=list)
        collect = InputChannel()

        def external_transition(self, inputs: Input):
            self.events.append(inputs[self.collect])

    # Define the state of the queue as a structured object
    class QueueState:
        def __init__(self, outputs):
            # Keep a list of all idle processors
            self.idle_procs = range(outputs)
            # Keep a list that is the actual queue data structure
            self.queue = []
            # Keep the process that is currently being processed
            self.processing = None
            # Time remaining for this event
            self.remaining_time = float("inf")

    class Queue(Atomic):
        queue: list[Any] = StateVariable(default_factory=list)
        idle_processors: list[Any] = StateVariable(default_factory=list)
        processing_time: float = StateConstant(1.0)

        enqueue = InputChannel()
        finish = InputChannel()

        def __init__(self, outputs):
            AtomicDEVS.__init__(self, "Queue")
            # Fix the time needed to process a single event
            self.processing_time = 1.0
            self.state = QueueState(outputs)

            # Create 'outputs' output ports
            # 'outputs' is a structural parameter!
            self.out_proc = []
            for i in range(outputs):
                self.out_proc.append(self.addOutPort("proc_%i" % i))

            # Add the other ports: incoming events and finished event
            self.in_event = self.addInPort("in_event")
            self.in_finish = self.addInPort("in_finish")

        def time_advance(self) -> Time:
            if self.queue and self.idle_processors:
                return self.processing_time
            else:
                return INFINITY

        def internal_transition(self):
            self.idle_processors.pop(0)
            if self.queue and self.idle_processors:
                self.processing = self.queue.pop(0)
            else:
                self.processing = None

        # def intTransition(self):
        #     # Is only called when we are outputting an event
        #     # Pop the first idle processor and clear processing event
        #     self.state.idle_procs.pop(0)
        #     if self.state.queue and self.state.idle_procs:
        #         # There are still queued elements, so continue
        #         self.state.processing = self.state.queue.pop(0)
        #         self.state.remaining_time = self.processing_time
        #     else:
        #         # No events left to process, so become idle
        #         self.state.processing = None
        #         self.state.remaining_time = float("inf")
        #     return self.state

        def external_transition(self, inputs: Input):
            if self.finish in inputs:
                self.idle_processors.append(inputs[self.finish])
                if not self.processing and self.queue:
                    # Process first task in queue
                    self.processing = self.queue.pop(0)
            elif self.enqueue in inputs:
                # Processing an incoming event
                if self.idle_processors and not self.processing:
                    # Process when idle processors
                    self.processing = inputs[self.enqueue]
                else:
                    # No idle processors, so queue it
                    self.queue.append(inputs[self.enqueue])

        # def output(self):
        #     ...

        # def outputFnc(self):
        #     # Output the event to the processor
        #     port = self.out_proc[self.state.idle_procs[0]]
        #     return {port: self.state.processing}
