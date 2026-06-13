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
from .schedule import DeviceLimitsSchedule
from .helpers import localise_datetime, standardise_datetime, API_TIMEZONE
from .utils import is_awaitable

_LOGGER = logging.getLogger(__name__)

class Account:
    """A family member with Digital Safety enabled.

    Attributes:
        user_id: Microsoft member identifier.
        role: Family role from the roster API.
        first_name: Member first name.
        surname: Member last name.
        profile_picture: Profile image URL.
        devices: Registered devices, populated by :meth:`update`.
        applications: Apps from the activity report, populated by :meth:`update`.
        today_screentime_usage: Total device screen time today in milliseconds.
        average_screentime_usage: Daily average screen time from the API.
        screentime_usage: Raw device screen-time report JSON.
        application_usage: Raw app activity report JSON.
        blocked_platforms: Platforms with an active device override block.
        account_balance: Microsoft Store allowance balance when available.
        account_currency: Currency code for ``account_balance``.
        experimental: Mirrors the parent :class:`FamilySafety` experimental flag.
    """

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
        begin_time, end_time = self._default_usage_time_range()
        (
            devices_response,
            device_usage,
            application_usage,
            overrides_response,
            _,
        ) = await asyncio.gather(
            self._api.async_get_user_devices(user_id=self.user_id),
            self._api.async_get_user_device_screentime_usage(
                user_id=self.user_id,
                begin_time=begin_time,
                end_time=end_time,
                device_count=4,
                platform="ALL",
            ),
            self._api.async_get_user_app_screentime_usage(
                user_id=self.user_id,
                begin_time=begin_time,
                end_time=end_time,
                platform="ALL",
            ),
            self._api.async_get_override_device_restrictions(user_id=self.user_id),
            self._get_account_balance(),
        )
        self._apply_screentime_usage(device_usage.get("json"), application_usage.get("json"))
        self.devices = Device.from_dict(devices_response.get("json"), self.screentime_usage)
        self._apply_applications()
        self._update_device_blocked(overrides_response.get("json"))
        for cb in self._account_callbacks:
            if is_awaitable(cb):
                await cb()
            else:
                cb()

    def _default_usage_time_range(self) -> tuple[str, str]:
        """Returns the default begin/end time query params for today's usage."""
        start_time = localise_datetime(datetime.combine(date.today(), time(0, 0, 0), tzinfo=API_TIMEZONE))
        end_time = localise_datetime(datetime.combine(date.today(), time(23, 59, 59), tzinfo=API_TIMEZONE))
        return (
            quote_plus(start_time.strftime('%Y-%m-%dT%H:%M:%S%z')),
            quote_plus(end_time.strftime('%Y-%m-%dT%H:%M:%S%z')),
        )

    def _apply_screentime_usage(self, device_usage: dict, application_usage: dict) -> None:
        """Store screentime usage payloads on the account."""
        self.screentime_usage = device_usage
        self.today_screentime_usage = device_usage["deviceUsageAggregates"]["totalScreenTime"]
        self.average_screentime_usage = device_usage["deviceUsageAggregates"]["dailyAverage"]
        self.application_usage = application_usage

    def _apply_applications(self) -> list[Application]:
        """Refresh application state from the latest activity report."""
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
        return self._apply_applications()

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
                                   device_count: int = 4,
                                   platform: str = "ALL") -> dict:
        """Return screen time usage for a time range.

        Args:
            start_time: Range start; defaults to start of today (local).
            end_time: Range end; defaults to end of today (local).
            device_count: Maximum devices in the device usage report.
            platform: Platform filter (e.g. ``ALL``, ``WINDOWS``, ``XBOX``).

        Returns:
            When default times are used, returns cached ``screentime_usage`` after
            updating account fields. Otherwise a dict with ``devices`` and
            ``applications`` keys containing raw JSON payloads.
        """
        default = False
        if start_time is None:
            default = True
            start_time = localise_datetime(datetime.combine(date.today(), time(0,0,0), tzinfo=API_TIMEZONE))
        if end_time is None:
            default = True
            end_time = localise_datetime(datetime.combine(date.today(), time(23,59,59), tzinfo=API_TIMEZONE))

        begin_time = quote_plus(start_time.strftime('%Y-%m-%dT%H:%M:%S%z'))
        end_time_param = quote_plus(end_time.strftime('%Y-%m-%dT%H:%M:%S%z'))

        device_usage, application_usage = await asyncio.gather(
            self._api.async_get_user_device_screentime_usage(
                user_id=self.user_id,
                begin_time=begin_time,
                end_time=end_time_param,
                device_count=device_count,
                platform=platform
            ),
            self._api.async_get_user_app_screentime_usage(
                user_id=self.user_id,
                begin_time=begin_time,
                end_time=end_time_param,
                platform=platform
            ),
        )

        if default:
            self._apply_screentime_usage(device_usage.get("json"), application_usage.get("json"))
            return self.screentime_usage
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

    async def set_device_limits(self, schedule: DeviceLimitsSchedule) -> dict:
        """Set screen time limits for a platform on the account.

        Args:
            schedule: Platform-specific limits built from
                :class:`~pyfamilysafety.schedule.DeviceLimitsSchedule`.

        Returns:
            The API response body, if present.
        """
        body = schedule.to_dict()
        body["time"] = localise_datetime(datetime.now()).strftime("%Y-%m-%dT%H:%M:%S%z")
        response = await self._api.async_update_schedule(
            user_id=self.user_id,
            body=body,
        )
        return response.get("json")

    async def override_device(self,
                              target: OverrideTarget,
                              override: OverrideType,
                              valid_until: datetime = None,
                              culture: str = "en-GB") -> bool:
        """Block or unblock a platform for this member.

        Args:
            target: Platform to override (:class:`~pyfamilysafety.enum.OverrideTarget`).
            override: ``OverrideType.UNTIL`` to block until a time, or
                ``OverrideType.CANCEL`` to remove a block.
            valid_until: Required when ``override`` is ``UNTIL``; ignored for
                ``CANCEL`` (set to now internally).
            culture: Locale string sent to the API (default ``en-GB``).

        Returns:
            ``True`` on success (implicit; method updates local block state).

        Raises:
            ValueError: If ``override`` is ``UNTIL`` and ``valid_until`` is omitted.
        """
        if override == OverrideType.UNTIL and valid_until is None:
            raise ValueError("valid_until is required if using OverrideType.UNTIL")
        if override == OverrideType.CANCEL:
            valid_until = datetime.now()
        response = await self._api.async_override_device_restriction(
            user_id=self.user_id,
            body={
                "target": str(target),
                "overrideType": str(override),
                "validUntil": standardise_datetime(valid_until).strftime("%Y-%m-%dT%H:%M:%S.000%z"),
                "culture": culture,
            }
        )
        self._update_device_blocked(response.get("json"))

    async def get_web_restrictions(self) -> dict:
        """Return current web filtering settings for this member.

        Returns:
            Parsed JSON from the web restrictions API.
        """
        response = await self._api.async_get_user_web_restrictions(user_id=self.user_id)
        return response.get("json")

    async def update_web_restrictions(self, operations: list[dict]) -> dict:
        """Apply web filtering changes using JSON Patch operations.

        Args:
            operations: List of patch operation dicts (``op``, ``path``, ``value``, etc.).

        Returns:
            Parsed JSON response from the API, if present.
        """
        response = await self._api.async_update_web_restrictions(
            user_id=self.user_id,
            body={"operations": operations},
        )
        return response.get("json")

    async def add_web_exception(
            self,
            website: str,
            allowed: bool = False,
            source: str = "") -> dict:
        """Add a web filtering exception for a specific website.

        Args:
            website: Domain or URL to except from the default filter.
            allowed: ``True`` to always allow; ``False`` to always block.
            source: Optional source label sent to the API.

        Returns:
            Parsed JSON response from the API, if present.
        """
        return await self.update_web_restrictions([{
            "op": "Add",
            "path": "/exceptions",
            "source": source,
            "value": {
                "website": website,
                "allowed": allowed,
            },
        }])

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
        accounts = []
        if "members" in raw_response.keys():
            members = raw_response.get("members")
            for member in members:
                if member.get("isDigitalSafetyEnabled"):
                    account = cls(api)
                    account.user_id = member.get("id")
                    account.role = member.get("role")
                    account.profile_picture = member.get("profilePicUrl")
                    account.first_name = member.get("user").get("firstName")
                    account.surname = member.get("user").get("lastName")
                    account.experimental = experimental
                    accounts.append(account)
            if accounts:
                await asyncio.gather(*(account.update() for account in accounts))

        return accounts
