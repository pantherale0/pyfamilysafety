"""Helper functions for pyfamilysafety."""

from datetime import datetime
from dateutil import tz

API_TIMEZONE = tz.tzutc()
LOCAL_TIMEZONE = tz.tzlocal()

def localise_datetime(dt: datetime) -> datetime:
    """Localise the datetime into the current timezone."""
    return dt.replace(tzinfo=LOCAL_TIMEZONE)

def standardise_datetime(dt: datetime) -> datetime:
    """Standardise the datetime into UTC."""
    return dt.replace(tzinfo=API_TIMEZONE)
