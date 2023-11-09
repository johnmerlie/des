from pydes.errors import InvalidInputError, InvalidStateError
from pydes.model import Discrete, Input, Model
from pydes.utils import INFINITY


class Interrupt(Discrete):
    toManual = 1
    toAutomatic = 2


class Observed(Discrete):
    grey = 1
    yellow = 2


class TrafficLightState(Discrete):
    red = 1
    yellow = 2
    green = 3
    manual = 4


class TrafficLight(Model[TrafficLightState, Interrupt, Observed]):
    States = TrafficLightState
    initial_state = TrafficLightState.red

    @classmethod
    def time_advance(cls, state: States):
        match state:
            case cls.States.red:
                return 60.0
            case cls.States.yellow:
                return 10.0
            case cls.States.green:
                return 50.0
            case cls.States.manual:
                return INFINITY

        raise InvalidStateError(state)

    @classmethod
    def external_transition(cls, state: States, inputs: Input[Interrupt]):
        match inputs.get(Interrupt):
            case Interrupt.toManual:
                match state:
                    case cls.States():
                        return cls.States.manual
                raise InvalidStateError(state)
            case Interrupt.toAutomatic:
                match state:
                    case cls.States.manual:
                        return cls.States.red
                    case cls.States():
                        return state
                raise InvalidStateError(state)
            case other:
                raise InvalidInputError(other)

    @classmethod
    def internal_transition(cls, state: States):
        match state:
            case cls.States.red:
                return cls.States.green
            case cls.States.green:
                return cls.States.yellow
            case cls.States.yellow:
                return cls.States.red
            case other:
                raise InvalidStateError(other)

    @classmethod
    def output(cls, state: States):
        match state:
            case cls.States.red:
                return {Observed: Observed.grey}
            case cls.States.green:
                return {Observed: Observed.yellow}
            case cls.States.yellow:
                return {Observed: Observed.grey}
            case other:
                raise InvalidStateError(other)


class PolicemanState(Discrete):
    idle = 1
    working = 2


class Policeman(Model[PolicemanState, None, Interrupt]):
    States = PolicemanState

    @classmethod
    def time_advance(cls, state: States):
        """
        Time-Advance Function.
        """
        match state:
            case cls.States.idle:
                return 200
            case cls.States.working:
                return 100
        raise InvalidStateError(state)

    @classmethod
    def internal_transition(cls, state: States):
        """
        Internal Transition Function.
        The policeman works forever, so only one mode.
        """

        match state:
            case cls.States.idle:
                return cls.States.working
            case cls.States.working:
                return cls.States.idle

        raise InvalidStateError(state)

    @classmethod
    def output(cls, state: States):
        """
        Output Funtion.
        """
        match state:
            case cls.States.idle:
                return {Interrupt: Interrupt.toManual}
            case cls.States.working:
                return {Interrupt: Interrupt.toAutomatic}
        raise InvalidStateError(state)
