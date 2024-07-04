import smbus2
import logging


class I2CDevice:
    def __init__(self, i2c_bus: smbus2.SMBus, i2c_addr: int):
        self.bus = i2c_bus
        self.addr = i2c_addr
        self.logger = logging.getLogger(__name__)

    def _read8(self, reg_addr: int) -> int:
        return self.bus.read_byte_data(i2c_addr=self.addr, register=reg_addr)

    def _read16(self, reg_addr: int) -> int:
        data = self.bus.read_i2c_block_data(
            i2c_addr=self.addr, register=reg_addr, length=2
        )
        return data[0] << 8 | data[1]

    def _write8(self, reg_addr: int, data: int) -> None:
        if data > 0xFF:
            raise ValueError(
                "Attempted to write value greater than 0xFF to 8 bit "
                f"register: {hex(data)} to register {hex(reg_addr)}."
            )
        self.bus.write_byte_data(
            i2c_addr=self.addr, register=reg_addr, value=(data & 0xFF)
        )

    def _write16(self, reg_addr: int, data: int) -> None:
        if data > 0xFFFF:
            raise ValueError(
                "Attempted to write value greater than 0xFFFF to 16 bit "
                f"register: {hex(data)} to register {hex(reg_addr)}."
            )
        data_bytes = [(data >> 8) & 0xFF, data & 0xFF]
        self.bus.write_i2c_block_data(
            i2c_addr=self.addr, register=reg_addr, data=data_bytes
        )
