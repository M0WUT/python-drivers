import pathlib


class GPIO:
    OUTPUT = 0
    INPUT = 1
    HIGH = 1
    LOW = 0

    def __init__(
        self, gpio: int, direction: bool | int, initial_value: bool | int
    ):
        """Base class for all GPIO pins"""

        self.gpio = gpio
        self.dir = pathlib.Path("/sys") / "class" / "gpio" / f"gpio{self.gpio}"

        if not self.dir.exists():
            # Only export GPIO if it doesn't already exist
            with open((self.dir.parent / "export"), "w") as file:
                file.write(str(self.gpio))

        self.set_direction(direction)

        if self.direction == GPIO.OUTPUT:
            self.write(initial_value)

    def set_direction(self, direction: bool | int) -> None:
        """Sets direction of GPIO pin"""
        with open(self.dir / "direction", "w+") as file:
            file.write("out" if direction == GPIO.OUTPUT else "in")
            self.direction = direction

    def write(self, value: bool | int) -> None:
        """
        Sets the state of an output GPIO. Does nothing if GPIO is
        configured as an input
        """
        if self.direction == GPIO.OUTPUT:
            with open(self.dir / "value", "w") as file:
                file.write("1" if value else "0")

    def read(self) -> bool:
        if self.direction == GPIO.INPUT:
            with open(self.dir / "value", "r") as file:
                return bool(int(file.read().strip()))
        else:
            return False


class AxiGpio(GPIO):

    BASE_ADDRESS = 1018

    def __init__(
        self,
        axiGpio: int,
        direction: bool | int = GPIO.INPUT,
        initial_value: bool | int = GPIO.LOW,
    ):
        super().__init__(
            gpio=axiGpio + self.BASE_ADDRESS,
            direction=direction,
            initial_value=initial_value,
        )


class MIO(GPIO):

    BASE_ADDRESS = 900

    def __init__(
        self,
        mio: int,
        direction: bool | int,
        initial_value: bool | int,
    ):
        super().__init__(
            gpio=mio + self.BASE_ADDRESS,
            direction=direction,
            initial_value=initial_value,
        )


class RPiGPIO(GPIO):
    BASE_ADDRESS = 512

    def __init__(
        self,
        gpio: int,
        direction: bool | int = GPIO.INPUT,
        initial_value: bool | int = GPIO.LOW,
    ):
        super().__init__(
            gpio=gpio + self.BASE_ADDRESS,
            direction=direction,
            initial_value=initial_value,
        )
