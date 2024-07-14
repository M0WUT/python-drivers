import pathlib
import logging


class DS2431:
    """
    Note that this is greedy and assumes a single device on the bus
    which is the EEPROM
    """

    def __init__(self):
        BASE_PATH = pathlib.Path("/sys") / "bus" / "w1" / "devices"
        self.file_path = [x for x in BASE_PATH.glob("eeprom")][0]
        assert self.file_path, "Could not find EEPROM"

    def read(self) -> str:
        return self.file_path.read_text()

    def write(self, data: str) -> None:
        self.file_path.write_text(data)

    def read_card_address(self):
        data = self.read()
        assert data[:3] == "LID", "Invalid EEPROM found"
        return int(data[3])
