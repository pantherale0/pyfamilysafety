"""Device limit schedule models.

Use these classes to build the payload for ``Account.set_device_limits``.
Limits apply to a platform (Desktop, Xbox, or Mobile) rather than a single device.
"""

from datetime import time

from .enum import DayOfWeek, DeviceLimitsMode, OverrideTarget


class AllottedInterval:
    """A time window when device use is permitted.

    Times use ``HH:MM:SS`` strings, or pass :class:`datetime.time` objects via
    :meth:`from_time`.
    """

    def __init__(self, begin: str, end: str) -> None:
        self.begin = begin
        self.end = end

    @classmethod
    def from_time(cls, begin: time, end: time) -> "AllottedInterval":
        """Build an interval from time objects."""
        return cls(
            begin=begin.strftime("%H:%M:%S"),
            end=end.strftime("%H:%M:%S"),
        )

    def to_dict(self) -> dict:
        """Convert to the API request format."""
        return {
            "begin": self.begin,
            "end": self.end,
        }


class DailyRestriction:
    """Screen time limits for a single day.

    ``allowance`` is the total permitted screen time in milliseconds.
    ``allotted_intervals`` optionally restricts use to specific time windows.
    """

    def __init__(
            self,
            allowance: int,
            allotted_intervals: list[AllottedInterval] = None) -> None:
        self.allowance = allowance
        self.allotted_intervals = allotted_intervals or []

    @classmethod
    def from_minutes(
            cls,
            allowance_minutes: int,
            allotted_intervals: list[AllottedInterval] = None) -> "DailyRestriction":
        """Build a restriction using an allowance in minutes."""
        return cls(
            allowance=int(allowance_minutes * 60 * 1000),
            allotted_intervals=allotted_intervals,
        )

    def to_dict(self) -> dict:
        """Convert to the API request format."""
        result = {"allowance": self.allowance}
        if self.allotted_intervals:
            result["allottedIntervals"] = [
                interval.to_dict() for interval in self.allotted_intervals
            ]
        return result


class DeviceLimitsSchedule:
    """Device screen time limits for a platform.

    Serialize with :meth:`to_dict` before sending to the API. Pass an instance
    directly to :meth:`pyfamilysafety.account.Account.set_device_limits`.
    """

    def __init__(
            self,
            platform: OverrideTarget,
            daily_restrictions: dict[DayOfWeek, DailyRestriction],
            mode: DeviceLimitsMode = DeviceLimitsMode.PER_DEVICE_TYPE,
            culture: str = "en-GB") -> None:
        self.platform = platform
        self.daily_restrictions = daily_restrictions
        self.mode = mode
        self.culture = culture

    def to_dict(self) -> dict:
        """Convert to the API request format."""
        return {
            "dailyRestrictions": {
                str(day): restriction.to_dict()
                for day, restriction in self.daily_restrictions.items()
            },
            "mode": str(self.mode),
            "appliesTo": str(self.platform),
            "culture": self.culture,
        }
