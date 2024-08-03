import subprocess
import re


class RaspberryPi4:
    def __init__(self) -> None:
        pass

    def read_cpu_temperature(self) -> float:
        temperature = subprocess.check_output(
            ["cat", "/sys/class/thermal/thermal_zone0/temp"]
        )
        return float(temperature) / 1000

    def read_memory_usage_percent(self) -> int:
        """Returns total RAM in bytes"""
        results = (
            subprocess.check_output(["cat", "/proc/meminfo"]).strip().decode()
        )
        memstats = {}
        results = [re.split(r"\s+", x[:-3]) for x in results.split("\n")]
        for item in results:
            key = item[0][:-1]
            value = item[1]
            memstats[key] = int(value)
        return int(100 * (1 - memstats["MemAvailable"] / memstats["MemTotal"]))


def main() -> None:
    x = RaspberryPi4()
    print(x.read_memory_usage_percent())


if __name__ == "__main__":
    main()
