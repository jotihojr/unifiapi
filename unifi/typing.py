import re
from enum import StrEnum


class ApiTarget(StrEnum):
    OS = "console"
    NETWORK = "network"
    PROTECT = "protect"


class PoeMode(StrEnum):
    OFF = "off"
    ON = "auto"
    AUTO = "auto"
    UNKNOWN = "nodef"


class MacAddr:
    macre = r"^([0-9a-f]{2}(?::[0-9a-f]{2}){5})$"

    def __init__(self, addr: str):
        if not re.match(self.macre, addr, re.IGNORECASE):
            raise ValueError(f"invalid mac address '{addr}'")
        self.__mac = addr.lower()

    @property
    def value(self) -> str:
        return self.__mac

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__mac == other.__mac
        elif isinstance(other, str):
            return self.__mac == other.lower()
        return False

    def __hash__(self):
        return self.__mac.__hash__()

    def __repr__(self):
        return f"{self.__class__.__name__}('{self.__mac}')"

    def __str__(self):
        return self.__mac
