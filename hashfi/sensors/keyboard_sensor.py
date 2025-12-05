import sys
import select
import termios
import tty
from hashfi.sensors.base import BaseSensor


class KeyboardPanicSensor(BaseSensor):
    def __init__(self):
        super().__init__(
            name="Keyboard Panic", weight=10.0
        )  # High weight to trigger immediately
        self.triggered = False

    def check_threat(self) -> float:
        if self.triggered:
            return 1.0

        # Check for input without blocking
        if self.is_data():
            c = sys.stdin.read(1)
            if c == "p":  # 'p' for PANIC
                self.triggered = True
                return 1.0
        return 0.0

    def is_data(self):
        return select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], [])

    def reset(self):
        self.triggered = False
