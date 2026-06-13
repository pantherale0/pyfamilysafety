"""Family Safety enums."""

from enum import Enum

class OverrideTarget(Enum):
    """Platform target for device limits and override actions.

    Attributes:
        DESKTOP: Windows PCs and similar desktop devices.
        XBOX: Xbox consoles.
        MOBILE: Phones and tablets.
    """
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
    def from_pretty(cls, pretty: str) -> 'OverrideTarget':
        """Parse an API display string into an enum member.

        Args:
            pretty: One of ``Desktop``, ``Mobile``, or ``Xbox``.
        """
        if pretty == "Desktop":
            return cls.DESKTOP
        if pretty == "Mobile":
            return cls.MOBILE
        if pretty == "Xbox":
            return cls.XBOX

class OverrideType(Enum):
    """How to apply a device override (block or unblock).

    Attributes:
        CANCEL: Remove an active block immediately.
        UNTIL: Block until a given ``valid_until`` datetime.
    """
    CANCEL = 0
    UNTIL = 1

    def __str__(self) -> str:
        if self.name == "CANCEL":
            return "Cancel"
        if self.name == "UNTIL":
            return "BlockUntil"
        return self.name

class DayOfWeek(Enum):
    """Days used in device limit schedules.

    Serialized as lowercase English day names (``monday``, ``tuesday``, …).
    """
    MONDAY = "monday"
    TUESDAY = "tuesday"
    WEDNESDAY = "wednesday"
    THURSDAY = "thursday"
    FRIDAY = "friday"
    SATURDAY = "saturday"
    SUNDAY = "sunday"

    def __str__(self) -> str:
        return self.value

class DeviceLimitsMode(Enum):
    """How device limits are applied to a platform schedule.

    Attributes:
        PER_DEVICE_TYPE: Limits apply per device type (default API mode).
    """
    PER_DEVICE_TYPE = "PerDeviceType"

    def __str__(self) -> str:
        return self.value
