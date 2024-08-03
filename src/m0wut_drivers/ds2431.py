import pathlib
import logging


class DS2431:
    """
    Note that this is greedy and assumes a single device on the bus
    which is the EEPROM
    """

    def __init__(self):
        BASE_PATH = pathlib.Path("/sys") / "bus" / "w1" / "devices"
        eeprom_paths = []
        for folder in BASE_PATH.iterdir():
            eeprom_paths += [x for x in folder.glob("eeprom")]
        if len(eeprom_paths) != 1:
            raise NotImplementedError(eeprom_paths)
        self.file_path = eeprom_paths[0]
        assert self.file_path, "Could not find EEPROM"

    def read(self) -> list[bytes]:
        return self.file_path.read_bytes()

    def write(self, data: list[bytes]) -> None:
        self.file_path.write_bytes(data)

    def read_card_address(self):
        data = self.read()
        assert data[:3] == b"LID", "Invalid EEPROM found"
        return int(data[3])
