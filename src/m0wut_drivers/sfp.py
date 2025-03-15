# Standard imports
from dataclasses import dataclass
import logging
from typing import Optional

# Third-party imports
import smbus2

# Local imports
from m0wut_drivers.i2c_device import I2CDevice
from m0wut_drivers.gpio import GPIO, RPiGPIO


@dataclass()
class SFPInfo:
    sfpType: str
    manufacturer: str
    partNumber: str
    revision: str


class SFP:
    def __init__(
        self,
        i2c_bus: smbus2.SMBus,
        i2c_addr: int,
        gpio_presetn: Optional[GPIO] = None,
        gpio_tx_enable: Optional[GPIO] = None,
        gpio_tx_fault: Optional[GPIO] = None,
        gpio_los: Optional[GPIO] = None,
        logger: Optional[logging.Logger] = None,
    ):
        self.dev = I2CDevice(i2c_bus=i2c_bus, i2c_addr=i2c_addr)
        self.logger = logger if logger else logging.getLogger(__name__)
        self.gpio_presentn = gpio_presetn
        self.gpio_tx_enable = gpio_tx_enable
        self.gpio_tx_fault = gpio_tx_fault
        self.gpio_los = gpio_los

    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        for gpio in [
            self.gpio_presentn,
            self.gpio_tx_enable,
            self.gpio_tx_fault,
            self.gpio_los,
        ]:
            if gpio:
                gpio.__exit__()
            self.dev.bus.close()

    def is_present(self) -> bool:
        """
        Checks the presence detect pin
        Return true if present (pin is low) OR present pin is not configured
        """
        if self.gpio_presentn is None:
            self.logger.warning(
                "Attempting to check if SFP connnector present but presence detect pin was not configured"
            )
            return True
        else:
            return not self.gpio_presentn.read()

    def tx_fault(self) -> bool:
        """
        Checks for a TX Fault
        Return true if fault (pin is high)
        Returns False if no fault OR present pin is not configured
        """
        if self.gpio_tx_fault is None:
            self.logger.warning(
                "Attempting to check for SFP TX Fault but TX Fault pin was not configured"
            )
            return False
        else:
            return self.gpio_tx_fault.read()

    def valid_rx_signal(self) -> bool:
        if self.gpio_los is None:
            self.logger.warning(
                "Attempting to check for SFP RX LOS but LOS pin was not configured"
            )
            return True
        else:
            return not self.gpio_los.read()

    def set_tx_enable_state(self, enabled: bool) -> None:
        assert (
            self.gpio_tx_enable
        ), "Attempted to set unconfigured TX Enable pin"
        self.gpio_tx_enable.write(enabled)

    def enable_tx(self):
        self.set_tx_enable_state(True)

    def disable_tx(self):
        self.set_tx_enable_state(False)

    def _is_compatible_eeprom(self) -> bool:
        if self.dev._read8(0) != 3 or self.dev._read8(1) != 4:
            # Reg 0 = 3: Connector is SFP (really hope this is true!)
            # Reg 1 = 4: Extended identifier - should be 4 for all SFP modules
            self.logger.error("Incompatible EEPROM found")
            return False
        else:
            return True

    def _read_sfp_type(self) -> str:
        result = self.dev._read8(2)
        if result == 7:
            return "LC"
        else:
            self.logger.warning(f"Unknown SFP Type: {result} found")
            return "Unknown"

    def _read_str(self, start_addr: int, end_addr: int) -> str:
        # Reads bytes from start_addr to end_addr inclusive
        # and returns as string with padding removed
        result = ""
        for x in range(start_addr, end_addr + 1):
            result += chr(self.dev._read8(x))
        return result.strip()

    def _read_manufacturer(self) -> str:
        return self._read_str(20, 35)

    def _read_part_number(self) -> str:
        return self._read_str(40, 55)

    def _read_revision(self) -> str:
        return self._read_str(56, 59)

    def read_sfp_info(self) -> Optional[SFPInfo]:
        if not self.is_present():
            return None

        if not self._is_compatible_eeprom():
            return None

        return SFPInfo(
            sfpType=self._read_sfp_type(),
            manufacturer=self._read_manufacturer(),
            partNumber=self._read_part_number(),
            revision=self._read_revision(),
        )


def main():
    with smbus2.SMBus(4) as bus, RPiGPIO(19) as sfp_presentn:
        x = SFP(i2c_bus=bus, i2c_addr=0x50, gpio_presetn=sfp_presentn)
        print(x.read_sfp_info())


if __name__ == "__main__":
    main()
