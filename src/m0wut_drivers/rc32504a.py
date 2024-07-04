from __future__ import annotations

import smbus2
from m0wut_drivers.i2c_device import I2CDevice
import logging


class RC32504AChannel:
    def __init__(self, parent_device: RC32504A, channel_number: int):
        if not 0 <= channel_number <= 3:
            raise ValueError("Channel number on RC32504A must be between 0-3")
        self.parent_device = parent_device


class RC32504A(I2CDevice):

    # Global Block Registers
    REG_VENDOR_ID = 0x00
    REG_DEVICE_ID = 0x02
    REG_DEVICE_REV = 0x04
    REG_DEVICE_PGM = 0x06
    REG_DEVICE_CNFG = 0x08
    REG_DEVICE_RESET = 0x0A
    REG_SW_RESET = 0x0C
    REG_CLOCK_GATE = 0x0E
    REG_DEVICE_STS = 0x10
    # Interrupt Block Registers
    REG_INT_EN = 0x20
    REG_INT_STS = 0x22
    # Loss of Signal Monitor Block Registers
    REG_LOSMON_STS = 0x30
    REG_LOSMON_EVENT = 0x31
    REG_LOSMON_QUAL = 0x32
    REG_LOSMON_WINDOW = 0x34
    REG_LOSMON_THRESH = 0x38
    REG_LOSMON_NOMINAL = 0x3C
    # Activity Monitor Block Registers
    REG_ACTMON_STS = 0x60
    REG_ACTMON_EVENT = 0x61
    REG_ACTMON_WINDOW = 0x64
    REG_ACTMON_THRESH = 0x68
    REG_ACTMON_NOMINAL = 0x70
    # DPLL Block Registers
    REG_DPLL_REF_FB_CNFG = 0xA0
    REG_DPLL_MODE = 0xA1
    REG_DPLL_DECIMATOR = 0xA2
    REG_DPLL_TRIM_OFFSET = 0xA3
    REG_DPLL_HOLDOVER_CNFG = 0xA4
    REG_DPLL_BANDWODTH = 0xA6
    REG_DPLL_DAMPING = 0xA8
    REG_DPLL_PHASE_SLOPE_LIMIT = 0xAC
    REG_DPLL_FB_DIV_NUM = 0xB0
    REG_DPLL_FB_DIV_DEN = 0xB8
    REG_DPLL_FB_DIV_INT = 0xC0
    REG_DPLL_FB_CORR = 0xC2
    REG_DPLL_HASE_OFFSET = 0xC4
    REG_DPLL_WRITE_FREQ = 0xC8
    REG_DPLL_LOCK = 0xCC
    REG_DPLL_TDC_DELAY = 0xD0
    REG_DPLL_STS = 0xD1
    REG_DPLL_EVENT = 0xD2
    REG_DPLL_LOL_CNT = 0xD3
    # RDC Block Registers
    REG_TDC_REG_DIC_CNFG = 0xE2
    REG_TDC_FB_SDM_CNFG = 0xE3
    REG_TDC_FB_DIV_INT = 0xE4
    REG_TDC_FB_DIV_FRAC = 0xE6
    REG_TDC_DAC_CNFG = 0xEA
    # System Clock Divider Block Registers
    REG_SYS_DIV_INT = 0xF0
    # Bias Block Registers
    REG_BIAS_STS = 0xF6
    # Crystal Block Registers
    REG_XO_CNFG = 0xF8
    # Clock0 Output Block Registers
    REG_OD_CNFG0 = 0x100
    REG_ODRV_EN0 = 0x102
    REG_ODRV_MODE_CNFG0 = 0x103
    REG_ODRV_AMP_CNFG0 = 0x104
    # Clock1 Output Block Registers
    REG_OD_CNFG1 = 0x108
    REG_ODRV_EN1 = 0x10A
    REG_ODRV_MODE_CNFG1 = 0x10B
    REG_ODRV_AMP_CNFG1 = 0x10C
    # Clock2 Output Block Registers
    REG_OD_CNFG2 = 0x110
    REG_ODRV_EN2 = 0x112
    REG_ODRV_MODE_CNFG2 = 0x113
    REG_ODRV_AMP_CNFG2 = 0x114
    # Clock3 Output Block Registers
    REG_OD_CNFG3 = 0x118
    REG_ODRV_EN3 = 0x11A
    REG_ODRV_MODE_CNFG3 = 0x11B
    REG_ODRV_AMP_CNFG3 = 0x11C
    # Clock Reference Block Registers
    REG_PREDIV_CNFG = 0x120
    # GPIO Block Registers
    REG_OE_CNFG = 0x130
    REG_IO_CNFG = 0x131
    REG_LOCK_CNFG = 0x132
    REG_STARTUP_STS = 0x137
    REG_GPIO_STS = 0x138
    REG_GPIO_SCRATCH0 = 0x13C
    # SSI Registers
    REG_SPI_CNFG = 0x140
    REG_I2C_FLTR_CNFG = 0x141
    REG_I2C_TIMING_CNFG = 0x142
    REG_I2C_ADDR_CNFG = 0x143
    REG_SSI_GLOBACL_CNFG = 0x144
    # APLL Registers
    REG_APLL_FB_DIV_FRAC = 0x150
    REG_APLL_FB_DIV_INT = 0x154
    REG_APLL_FB_SDM_CNFG = 0x156
    REG_APLL_CNFG = 0x157
    REG_LPF_CNFG = 0x15A
    REG_LPF_3RD_CNFG = 0x15B
    REG_APLL_LOCK_CNFG = 0x164
    REG_APLL_LOCK_THRSH = 0x166
    REG_VCO_CAL_STS = 0x167
    REG_APLL_STS = 0x168
    REG_APLL_EVENT = 0x169
    REG_APLL_LOL_CNT = 0x16A
    # Clock Input Registers
    REG_REF_CLK_IN_CNFG = 0x190

    # Constants
    EXPECTED_DEVICE_ID = 0x304A
    EXPECTED_DEVICE_REVISION = 0x0232

    def __init__(self, i2c_bus: smbus2.SMBus, i2c_addr: int):
        super().__init__(i2c_bus=i2c_bus, i2c_addr=i2c_addr)
        self.logger = logging.getLogger(__name__)
        assert self._read16(self.REG_DEVICE_ID) == self.EXPECTED_DEVICE_ID
        x = self._read16(self.REG_DEVICE_REV)
        if x != self.EXPECTED_DEVICE_REVISION:
            self.logger.warning(
                "Unexpected device revision on RC32504A. "
                f"Expected: {hex(self.EXPECTED_DEVICE_REVISION)}, got {hex(x)}"
            )

        self._channels = [
            RC32504AChannel(parent_device=self, channel_number=0),
            RC32504AChannel(parent_device=self, channel_number=1),
            RC32504AChannel(parent_device=self, channel_number=2),
            RC32504AChannel(parent_device=self, channel_number=3),
        ]

    def get_channel(self, channel_number: int) -> RC32504AChannel:
        try:
            return self._channels[channel_number]
        except IndexError:
            raise ValueError(
                f"Requested channel must be between 0-3. Got {channel_number}"
            )

    def get_channels(self) -> list[RC32504AChannel]:
        return self._channels


def main():
    pass


if __name__ == "__main__":
    main()
