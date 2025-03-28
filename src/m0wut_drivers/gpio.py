# Standard imports
import pathlib
import time
from enum import Enum, auto

# Third-party imports

# Local imports


class Polarity(Enum):
    ACTIVE_HIGH = 0
    ACTIVE_LOW = 1


class GPIO:
    OUTPUT = 0
    INPUT = 1
    ASSERTED = 1
    DEASSERTED = 0

    def __init__(
        self,
        gpio: int,
        direction: bool | int,
        polarity: Polarity = Polarity.ACTIVE_HIGH,
    ):
        """Base class for all GPIO pins"""
        self.gpio = gpio
        self.dir = pathlib.Path("/sys") / "class" / "gpio" / f"gpio{self.gpio}"

        self.direction = direction
        self._value = self.DEASSERTED
        self.active_low: bool = bool(polarity == Polarity.ACTIVE_LOW)

        if not self.dir.exists():
            # Only export GPIO if it doesn't already exist
            with open((self.dir.parent / "export"), "w") as file:
                file.write(str(self.gpio))

        # There is a processor dependant delay between writing a gpio to export
        # and the folder being available to write to. This is a nasty hack but hey!
        for i in range(5):
            try:
                self.set_direction(self.direction)
            except PermissionError:
                time.sleep(1)
                assert i < 4, "Failed to write to GPIO file"

    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        if self.direction == GPIO.OUTPUT:
            self.write(self.DEASSERTED)
        with open((self.dir.parent / "unexport"), "w") as file:
            file.write(str(self.gpio))

    def set_direction(self, direction: bool | int) -> None:
        """Sets direction of GPIO pin"""
        with open(self.dir / "direction", "w") as file:
            file.write("out" if direction == GPIO.OUTPUT else "in")
            self.direction = direction

    def write(self, value: bool | int) -> None:
        """
        Sets the state of an output GPIO.
        Setting value to True will assert the pin, polarity is handled automatically
        """
        assert (
            self.direction == GPIO.OUTPUT
        ), f"Attempted to set state of GPIO {self.gpio} which is configured as an input"
        with open(self.dir / "value", "w") as file:
            file.write("1" if (value ^ self.active_low) else "0")
            self._value = bool(value)

    def read(self) -> bool:
        """
        Returns true if GPIO is asserted (not what logic level is on it)
        """
        if self.direction == GPIO.INPUT:
            with open(self.dir / "value", "r") as file:
                return bool(int(file.read().strip())) ^ self.active_low
        else:
            return False

    def toggle(self) -> None:
        self.write(not self._value)


class AxiGpio(GPIO):

    BASE_ADDRESS = 1018

    def __init__(
        self,
        axiGpio: int,
        direction: bool | int = GPIO.INPUT,
        polarity=Polarity.ACTIVE_HIGH,
    ):
        super().__init__(
            gpio=axiGpio + self.BASE_ADDRESS,
            direction=direction,
            polarity=polarity,
        )


class MIO(GPIO):

    BASE_ADDRESS = 900

    def __init__(
        self,
        mio: int,
        direction: bool | int = GPIO.INPUT,
        polarity=Polarity.ACTIVE_HIGH,
    ):
        super().__init__(
            gpio=mio + self.BASE_ADDRESS,
            direction=direction,
            polarity=polarity,
        )


class RPiGPIO(GPIO):
    BASE_ADDRESS = 512

    def __init__(
        self,
        gpio: int,
        direction: bool | int = GPIO.INPUT,
        polarity=Polarity.ACTIVE_HIGH,
    ):
        super().__init__(
            gpio=gpio + self.BASE_ADDRESS,
            direction=direction,
            polarity=polarity,
        )
