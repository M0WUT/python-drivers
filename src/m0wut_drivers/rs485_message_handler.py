from dataclasses import dataclass
from m0wut_drivers.gpio import GPIO
from m0wut_drivers.misc import DeviceNotFoundError
import serial
from pathlib import Path


@dataclass
class RS485Packet:
    address: int
    command: str
    payload: str


class MessageHandler:
    TX = 1
    RX = 0

    def __init__(
        self, serial_file: Path, baud: int, trx_gpio: GPIO, rs485_addr: int
    ):

        try:
            self.serial = serial.Serial(
                str(serial_file.absolute()), baud, timeout=0.2
            )
        except serial.SerialException:
            raise DeviceNotFoundError(serial_file)

        self.gpio = trx_gpio
        self.gpio.set_direction(GPIO.OUTPUT)
        self.gpio.write(GPIO.LOW)
        self.rs485_addr = rs485_addr

        self.set_direction(self.RX)
        self.serial.reset_input_buffer()

    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        self.gpio.write(GPIO.LOW)
        self.serial.reset_input_buffer()
        self.serial.reset_output_buffer()

    def set_direction(self, x: bool | int):
        self.gpio.write(x)

    def write(self, x: RS485Packet):
        address = x.address.to_bytes(1, "big")
        command = x.command.encode("utf-8")
        self.set_direction(self.TX)
        payload = x.payload.encode("utf-8")

        self.serial.write(address + command + payload + b"\n")
        self.serial.flush()
        self.set_direction(self.RX)

        # Changing RS485 from TX to RX introduces glitches on the
        # RX line so clear the buffer
        self.serial.reset_input_buffer()

    def read(self) -> str:
        x = self.serial.readline()
        if x == b"":
            return ""

        if x[0] != self.rs485_addr:
            return ""

        return x.decode()[1:]  # Remove address character

    def query(self, packet: RS485Packet) -> str:
        self.write(packet)
        response = self.read()
        return response
