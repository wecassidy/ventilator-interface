import enum

import gpiozero as g0


class RotaryEncoder:
    """Based on https://bobrathbone.com/raspberrypi/documents/Raspberry%20Rotary%20Encoders.pdf"""

    def __init__(self, pinA, pinB, cwCallback, ccwCallback):
        self.btnA = g0.DigitalInputDevice(pinA, pull_up=False, bounce_time=0.05)
        self.btnA.when_activated = self.on_turn
        self.btnA.when_deactivated = self.on_turn

        self.btnB = g0.DigitalInputDevice(pinB, pull_up=False, bounce_time=0.05)
        self.btnB.when_activated = self.on_turn
        self.btnB.when_deactivated = self.on_turn

        self.lastState = self.get_state_code()
        self.onCW = cwCallback
        self.onCCW = ccwCallback

    def get_state_code(self):
        return (
            self.btnA.value << 2
            | self.btnB.value << 1
            | self.btnA.value ^ self.btnB.value
        )

    def on_turn(self):
        newState = self.get_state_code()
        delta = (newState - self.lastState) % 4
        self.lastState = newState

        if delta == 1:
            self.onCW()
        elif delta == 3:
            self.onCCW()


class Direction(enum.Enum):
    CW = enum.auto()
    CLOCKWISE = CW
    DOWN = CW

    CCW = enum.auto()
    COUNTERCLOCKWISE = CCW
    UP = CCW
