# pylint: disable=line-too-long
"""Family safety account handler."""

import asyncio
import logging
from datetime import datetime, date, time
from urllib.parse import quote_plus

from .api import FamilySafetyAPI
from .device import Device
from .application import Application
from .enum import OverrideTarget, OverrideType
from .helpers import localise_datetime, API_TIMEZONE
from .utils import is_awaitable

_LOGGER = logging.getLogger(__name__)

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
        self.applications: list[Application] = []
        self.today_screentime_usage: int = None
        self.average_screentime_usage: float = None
        self.screentime_usage: dict = None
        self.application_usage: dict = None
        self.blocked_platforms: list[OverrideTarget] = None
        self.experimental: bool = False
        self._api: FamilySafetyAPI = api
        self.account_balance: float = 0.0
        self.account_currency: str = ""
        self._account_callbacks: list = []

    def add_account_callback(self, callback):
        """Add a callback to the account."""
        if not callable(callback):
            raise ValueError("Object must be callable.")
        if callback not in self._account_callbacks:
            self._account_callbacks.append(callback)

    def remove_account_callback(self, callback):
        """Remove a given account callback."""
        if not callable(callback):
            raise ValueError("Object must be callable.")
        if callback in self._account_callbacks:
            self._account_callbacks.remove(callback)

    async def update(self) -> None:
        """Update all account details."""
        await self.get_screentime_usage()
        coros = [self._get_devices(), self._get_overrides(), self._get_applications(), self._get_account_balance()]
        await asyncio.gather(*coros)
        for cb in self._account_callbacks:
            if is_awaitable(cb):
                await cb()
            else:
                cb()

    async def _get_devices(self) -> list[Device]:
        """Returns all devices on the account."""
        response = await self._api.async_get_user_devices(user_id=self.user_id)
        self.devices = Device.from_dict(response.get("json"), self.screentime_usage)
        return self.devices

    async def _get_overrides(self):
        """Collects overrides."""
        response = await self._api.async_get_override_device_restrictions(
            user_id=self.user_id)
        self._update_device_blocked(response.get("json"))

    async def _get_applications(self) -> list[Application]:
        """Returns all applications on the account."""
        if self.application_usage is None:
            raise ValueError("Application usage not collected, call 'get_screentime_usage' first.")
        parsed_applications = Application.from_app_activity_report(
            self.application_usage,
            self._api,
            self.user_id)
        for app in parsed_applications:
            try:
                self.get_application(app.app_id).update(app)
            except IndexError:
                self.applications.append(app)
        return self.applications

    async def _get_account_balance(self):
        """Updates the account balance."""
        response = await self._api.async_get_user_spending(
            user_id=self.user_id
        )
        response = response["json"]
        balances = response.get("balances", [])
        if len(balances) == 1:
            self.account_balance = balances[0]["balance"]
            self.account_currency = balances[0]["currency"]

    async def get_screentime_usage(self,
                                   start_time: datetime = None,
                                   end_time: datetime = None,
                                   device_count = 4,
                                   platform: str = "ALL") -> dict:
        """Returns screentime usage for the account."""
        default = False
        if start_time is None:
            default = True
            start_time = localise_datetime(datetime.combine(date.today(), time(0,0,0), tzinfo=API_TIMEZONE))
        if end_time is None:
            default = True
            end_time = localise_datetime(datetime.combine(date.today(), time(23,59,59), tzinfo=API_TIMEZONE))

        device_usage = await self._api.async_get_user_device_screentime_usage(
                user_id=self.user_id,
                begin_time=quote_plus(start_time.strftime('%Y-%m-%dT%H:%M:%S%z')),
                end_time=quote_plus(end_time.strftime('%Y-%m-%dT%H:%M:%S%z')),
                device_count=device_count,
                platform=platform
            )

        application_usage = await self._api.async_get_user_app_screentime_usage(
                user_id=self.user_id,
                begin_time=quote_plus(start_time.strftime('%Y-%m-%dT%H:%M:%S%z')),
                end_time=quote_plus(end_time.strftime('%Y-%m-%dT%H:%M:%S%z')),
                platform=platform
            )

        if default:
            self.screentime_usage = device_usage.get("json")
            self.today_screentime_usage = self.screentime_usage["deviceUsageAggregates"]["totalScreenTime"]
            self.average_screentime_usage = self.screentime_usage["deviceUsageAggregates"]["dailyAverage"]
            self.application_usage = application_usage.get("json")
            return self.screentime_usage
        else:
            # don't actually set a value
            return {
                "devices": device_usage.get("json"),
                "applications": application_usage.get("json")
            }

    def get_device(self, device_id) -> Device:
        """Returns a single device."""
        return [x for x in self.devices if x.device_id == device_id][0]

    def get_application(self, application_id) -> Application:
        """Returns a single application."""
        return [x for x in self.applications if x.app_id == application_id][0]

    async def override_device(self,
                              target: OverrideTarget,
                              override: OverrideType,
                              valid_until: datetime = None) -> bool:
        """Overrides a single device (block/unblock)"""
        if override == OverrideType.UNTIL and valid_until is None:
            raise ValueError("valid_until is required if using OverrideType.UNTIL")
        if override == OverrideType.CANCEL:
            valid_until = datetime.now()
        response = await self._api.async_override_device_restriction(
            user_id=self.user_id,
            body={
                "overrideType": str(override),
                "target": str(target),
                "validUntil": valid_until.strftime("%Y-%m-%dT%H:%M:%SZ")
            }
        )
        self._update_device_blocked(response.get("json"))

    def _update_device_blocked(self, raw_response: dict):
        """updates device(s) blocked status from a overrides response."""
        platforms = raw_response.get("lockablePlatforms")
        blocked_platforms = []
        for platform in platforms:
            # get if locked
            state = len(platform.get("overrides"))>0
            if state:
                blocked_platforms.append(OverrideTarget.from_pretty(platform.get("appliesTo")))

            for device in platform.get("devices"):
                try:
                    self.get_device(device.get("deviceId").replace("g:", "")).update_blocked_status(state)
                finally:
                    pass
        self.blocked_platforms = blocked_platforms

    @classmethod
    async def from_dict(cls, api: FamilySafetyAPI, raw_response: dict, experimental: bool) -> list['Account']:
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
                    self.experimental = experimental
                    await self.update()
                    response.append(self)

        return response
