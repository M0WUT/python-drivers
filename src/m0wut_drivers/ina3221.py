from __future__ import annotations

from m0wut_drivers.i2c_device import I2CDevice
import smbus2


class INA3221Channel:
    def __init__(
        self,
        parent_device: INA3221,
        channel_number: int,
        shunt_resistance: float,
    ):
        if not 0 <= channel_number <= 2:
            raise ValueError(f"Invalid channel number {channel_number}")
        self.parent_device = parent_device
        self.channel_number = channel_number
        self.shunt_resistance = shunt_resistance

    def read_voltage(self) -> float:
        return self.parent_device._read_bus_voltage(self.channel_number)

    def read_current(self) -> float:
        return (
            self.parent_device._read_shunt_voltage(self.channel_number)
            * self.shunt_resistance
        )


class INA3221:
    # Register map
    REG_CONFIG = 0x00
    REG_CH1_SHUNT_VOLTAGE = 0x01
    REG_CH1_BUS_VOLTAGE = 0x02
    REG_CH2_SHUNT_VOLTAGE = 0x03
    REG_CH2_BUS_VOLTAGE = 0x04
    REG_CH3_SHUNT_VOLTAGE = 0x05
    REG_CH3_BUS_VOLTAGE = 0x06
    REG_CH1_CRITICAL = 0x07
    REG_CH1_WARNING = 0x08
    REG_CH2_CRITICAL = 0x09
    REG_CH2_WARNING = 0x0A
    REG_CH3_CRITICAL = 0x0B
    REG_CH3_WARNING = 0x0C
    REG_SHUNT_VOLTAGE_SUM = 0x0D
    REG_SHUNT_VOLTAGE_SUM_LIMIT = 0x0E
    REG_MASK_ENABLE = 0x0F
    REG_POWER_VALID_UPPER_LIMIT = 0x10
    REG_POWER_VALID_LOWER_LIMIT = 0x11
    REG_MANUFACTURER_ID = 0xFE
    REG_DIE_ID = 0xFF

    # Helper arrays
    SHUNT_VOLTAGES = [
        REG_CH1_SHUNT_VOLTAGE,
        REG_CH2_SHUNT_VOLTAGE,
        REG_CH3_SHUNT_VOLTAGE,
    ]
    BUS_VOLTAGES = [
        REG_CH1_BUS_VOLTAGE,
        REG_CH2_BUS_VOLTAGE,
        REG_CH3_BUS_VOLTAGE,
    ]
    CRITICAL_LIMITS = [REG_CH1_CRITICAL, REG_CH2_CRITICAL, REG_CH3_CRITICAL]
    WARNING_LIMITS = [REG_CH1_WARNING, REG_CH2_WARNING, REG_CH3_WARNING]

    # Constants
    EXPECTED_MANUFACTURER_ID = 0x5449
    EXPECTED_DIE_ID = 0x3220
    SHUNT_VOLTAGE_PER_LSB = 40e-6
    BUS_VOLTAGE_PER_LSB = 8e-3
    VALID_CHANNELS = [1, 2, 3]

    def __init__(
        self,
        i2c_bus: smbus2.SMBus,
        i2c_addr: int,
        shunt_resistances: list[float],
    ):
        self.dev = I2CDevice(i2c_bus=i2c_bus, i2c_addr=i2c_addr)
        self._channels = [
            INA3221Channel(
                parent_device=self,
                channel_number=x,
                shunt_resistance=shunt_resistances[x - 1],
            )
            for x in self.VALID_CHANNELS
        ]
        assert (
            self.dev._read16(self.REG_MANUFACTURER_ID)
            == self.EXPECTED_MANUFACTURER_ID
        )
        assert self.dev._read16(self.REG_DIE_ID) == self.EXPECTED_DIE_ID

    def get_channels(self) -> list[INA3221Channel]:
        return self._channels

    def get_channel(self, channel_number: int) -> INA3221Channel:
        self.validate_channel_number(channel_number)
        return self._channels[channel_number - 1]

    def _read_voltage(self, reg_address: int) -> int:
        """
        Voltage registers have format [MSB:LSB] of
        [sign bit, 12 bits of value, 3 padding zeros]
        """
        data = self.dev._read16(reg_address)
        sign = -1 if data & (1 << 15) else 1
        return sign * ((data >> 3) & 0xFFF)

    def validate_channel_number(self, channel_number: int) -> None:
        assert channel_number in self.VALID_CHANNELS

    def _read_bus_voltage(self, channel_number: int) -> float:
        self.validate_channel_number(channel_number)
        voltage = (
            self._read_voltage(self.BUS_VOLTAGES[channel_number - 1])
            * self.BUS_VOLTAGE_PER_LSB
        )
        return voltage

    def _read_shunt_voltage(self, channel_number: int) -> float:
        self.validate_channel_number(channel_number)
        voltage = (
            self._read_voltage(self.SHUNT_VOLTAGES[channel_number - 1])
            * self.SHUNT_VOLTAGE_PER_LSB
        )
        return voltage


def main():
    with smbus2.SMBus(1) as bus:
        x = INA3221(
            i2c_bus=bus, i2c_addr=0x40, shunt_resistances=[56e-3, 56e-3, 0.15]
        )
        ch1 = x.get_channel(1)
        print(ch1.read_voltage())


if __name__ == "__main__":
    main()
