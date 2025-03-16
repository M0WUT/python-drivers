import subprocess
import re
import socket
from typing import Optional
from uuid import getnode


class LinuxCPU:
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

    def get_ip(self) -> Optional[str]:
        """Returns IP Address as string"""
        # Credit to Stack Overflow user2561747
        # https://stackoverflow.com/questions/166506/finding-local-ip-addresses-using-pythons-stdlib
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            # doesn't even have to be reachable
            s.connect(("10.255.255.255", 1))
            ip_addr = str(s.getsockname()[0])
        except Exception:
            ip_addr = None
        finally:
            s.close()
        return ip_addr

    def get_mac_address(self) -> str:
        mac = getnode()
        return ":".join(("%012X" % mac)[i : i + 2] for i in range(0, 12, 2))

    def get_link_speed(self, interface_name: str = "eth0") -> int:
        # Returns wired link speed in Mbps
        with open(f"/sys/class/net/{interface_name}/speed") as file:
            return int(file.readline().strip())


def main() -> None:
    x = LinuxCPU()
    print(f"CPU Temperature: {x.read_cpu_temperature()}C")
    print(f"RAM Usage: {x.read_memory_usage_percent()}%")
    print(f"IP Address: {x.get_ip()}")
    print(f"MAC Address: {x.get_mac_address()}")
    print(f"Link Speed: {x.get_link_speed()}Mbps")


if __name__ == "__main__":
    main()
