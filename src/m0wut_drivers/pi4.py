import subprocess


class RaspberryPi4:
    def __init__(self) -> None:
        pass

    def read_cpu_temperature(self) -> float:
        temperature = subprocess.check_output(
            ["cat", "/sys/class/thermal/thermal_zone0/temp"]
        )
        return float(temperature) / 1000


def main() -> None:
    x = RaspberryPi4()
    print(x.read_cpu_temperature())


if __name__ == "__main__":
    main()
