"""Defines a Microsoft Device."""

class Device:
    """A device registered to a family member.

    Attributes:
        device_id: Unique identifier (``g:`` prefix stripped).
        device_name: Friendly display name.
        device_class: Device class from the API.
        device_make: Hardware manufacturer.
        device_model: Hardware model name.
        form_factor: Form factor string (phone, console, etc.).
        os_name: Operating system name.
        today_time_used: Screen time today in milliseconds, if reported.
        issues: Raw issue list from the API.
        states: Raw state list from the API.
        last_seen: Last-seen timestamp from the API.
        blocked: Whether the device is blocked via a platform override.
    """

    def __init__(self) -> None:
        """Init a device."""
        self.device_id = None
        self.device_name = None
        self.device_class = None
        self.device_make = None
        self.device_model = None
        self.form_factor = None
        self.os_name = None
        self.today_time_used = None
        self.issues = None
        self.states = None
        self.last_seen = None
        self.blocked = None

    def read_screentime_report(self, screentime_report: dict):
        """Processes a screentime report."""
        usage = screentime_report.get("deviceUsageAggregates")
        device_usage = [x for x in usage.get("deviceAggregates") if x["deviceId"] == self.device_id]
        if len(device_usage) > 0:
            self.today_time_used = device_usage[0].get("timeUsed")

    def update_blocked_status(self, state: bool):
        """Updates the blocked status."""
        self.blocked = state

    @classmethod
    def from_dict(cls, raw_response: dict, screentime_report: dict) -> list['Device']:
        """Parse a raw response from 'get_user_devices' into a list."""
        devices = []
        if "devices" in raw_response.keys():
            for device in raw_response.get("devices"):
                self = cls()
                self.device_id = device.get("deviceId").replace("g:", "")
                self.device_name = device.get("deviceName")
                self.device_class = device.get("deviceClass")
                self.device_make = device.get("deviceMake")
                self.device_model = device.get("deviceModel")
                self.form_factor = device.get("deviceFormFactor")
                self.os_name = device.get("osName")
                self.issues = device.get("issues")
                self.states = device.get("states")
                self.last_seen = device.get("lastSeenOn")
                self.read_screentime_report(screentime_report)
                devices.append(self)
        return devices
