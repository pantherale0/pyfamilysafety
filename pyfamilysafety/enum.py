"""Family Safety enums."""

from enum import Enum

class OverrideTarget(Enum):
    """A list of targets to override the lock state."""
    DESKTOP = 0
    XBOX = 1
    MOBILE = 2

    def __str__(self) -> str:
        if self.name == "DESKTOP":
            return "Desktop"
        if self.name == "MOBILE":
            return "Mobile"
        if self.name == "XBOX":
            return "Xbox"
        return self.name

    @classmethod
    def from_pretty(cls, pretty) -> 'OverrideTarget':
        """Returns from pretty."""
        if pretty == "Desktop":
            return cls.DESKTOP
        if pretty == "Mobile":
            return cls.MOBILE
        if pretty == "Xbox":
            return cls.XBOX

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
