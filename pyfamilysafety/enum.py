"""Family Safety enums."""

from enum import Enum

class OverrideTarget(Enum):
    """A list of targets to override the lock state."""
    WINDOWS = 0
    XBOX = 1
    MOBILE = 2
    ALL_DEVICES = 4

    def __str__(self) -> str:
        if self.name == "ALL_DEVICES":
            return "AllDevices"
        if self.name == "WINDOWS":
            return "Windows"
        if self.name == "MOBILE":
            return "Mobile"
        if self.name == "XBOX":
            return "Xbox"
        return self.name

class OverrideType(Enum):
    """A list of override types."""
    CANCEL = 0
    UNTIL = 1

    def __str__(self) -> str:
        if self.name == "CANCEL":
            return "Cancel"
        if self.name == "UNTIL":
            return "BlockUntil"
        return self.name
