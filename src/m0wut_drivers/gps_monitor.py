import gpsd
from datetime import datetime
from dataclasses import dataclass

from enum import Enum


class GPSFixStatus(Enum):
    NO_VALUE = 0
    NO_FIX = (1,)
    FIX_2D = (2,)
    FIX_3D = 3


@dataclass
class GPSInfo:
    num_sats: int
    position: tuple[float, float]
    altitude: float
    time: datetime


class GPSMonitor:
    def __init__(self, host: str = "127.0.0.1", port: int = 2947) -> None:
        gpsd.connect(host, port)

    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        pass

    def get_number_of_sats(self) -> int:
        packet = gpsd.get_current()
        return packet.sats

    def get_position(self) -> tuple[float, float]:
        packet = gpsd.get_current()
        return packet.position()

    def get_altitude(self) -> float:
        packet = gpsd.get_current()
        return packet.altitude()

    def get_time(self) -> datetime:
        packet = gpsd.get_current()
        return packet.get_time()

    def get_info(self) -> GPSInfo:
        packet = gpsd.get_current()
        return GPSInfo(
            num_sats=packet.sats,
            position=packet.position(),
            altitude=packet.altitude(),
            time=packet.get_time(),
        )

    def get_fix_status(self) -> GPSFixStatus:
        packet = gpsd.get_current()
        return_value = {
            0: GPSFixStatus.NO_VALUE,
            1: GPSFixStatus.NO_FIX,
            2: GPSFixStatus.FIX_2D,
            3: GPSFixStatus.FIX_3D,
        }
        return return_value[packet.mode]


def main():
    x = GPSMonitor()
    print(x.get_number_of_sats())


if __name__ == "__main__":
    main()
