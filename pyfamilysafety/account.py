"""Family safety account handler."""

from datetime import datetime, date, time, timedelta

from .api import FamilySafetyAPI
from .device import Device

class Account:
    """Represents a single family safety account."""

    def __init__(self, api) -> None:
        """Init an account."""
        self.user_id = None
        self.role = None
        self.profile_picture = None
        self.first_name = None
        self.surname = None
        self.devices: list[Device] = None
        self.today_screentime_usage: int = None
        self.average_screentime_usage: float = None
        self.screentime_usage: dict = None
        self._api: FamilySafetyAPI = api

    async def update(self) -> None:
        """Update all account details."""
        await self.get_screentime_usage()
        await self.get_devices()

    async def get_devices(self) -> list[Device]:
        """Returns all devices on the account."""
        response = await self._api.send_request("get_user_devices", USER_ID=self.user_id)
        self.devices = Device.from_dict(response.get("json"), self.screentime_usage)
        return self.devices

    async def get_screentime_usage(self,
                                   start_time: datetime = None,
                                   end_time: datetime = None,
                                   device_count = 4) -> dict:
        """Returns screentime usage for the account."""
        default = False
        if start_time is None:
            default = True
            start_time = datetime.combine(date.today(), time(0,0,0))
        if end_time is None:
            default = True
            end_time = start_time + timedelta(hours=24)

        response = await self._api.send_request(
                endpoint="get_user_device_screentime_usage",
                USER_ID=self.user_id,
                BEGIN_TIME=start_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                END_TIME=end_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                DEVICE_COUNT=device_count
            )

        if default:
            self.screentime_usage = response.get("json")
            self.today_screentime_usage = self.screentime_usage["deviceUsageAggregates"]["totalScreenTime"]
            self.average_screentime_usage = self.screentime_usage["deviceUsageAggregates"]["dailyAverage"]
            return self.screentime_usage
        else:
            # don't actually set a value
            return response.get("json")

    def get_device(self, device_id) -> Device:
        """Returns a single device."""
        return [x for x in self.devices if x.device_id == device_id][0]

    @classmethod
    async def from_dict(cls, api: FamilySafetyAPI, raw_response: dict) -> list['Account']:
        """Converts a roster request response to an array."""
        response = []
        if "members" in raw_response.keys():
            members = raw_response.get("members")
            for member in members:
                if member.get("isDigitalSafetyEnabled"):
                    self = cls(api)
                    self.user_id = member.get("id")
                    self.role = member.get("role")
                    self.profile_picture = member.get("profilePicUrl")
                    self.first_name = member.get("user").get("firstName")
                    self.surname = member.get("user").get("lastName")
                    await self.update()
                    response.append(self)

        return response
