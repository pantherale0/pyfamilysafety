"""Microsoft Family Safety async Python client."""

import asyncio
import logging
from typing import Callable

from .authenticator import Authenticator
from .api import FamilySafetyAPI
from .account import Account
from .exceptions import AggregatorException
from .utils import is_awaitable
from ._version import __version__

_LOGGER = logging.getLogger(__name__)

class FamilySafety:
    """Main client for Microsoft Family Safety.

    Holds the authenticated API session, family member accounts, and optional
    pending screen-time request handling.

    Attributes:
        accounts: Family members with Digital Safety enabled, populated after
            the first :meth:`update`.
        experimental: When ``True``, :meth:`update` fetches pending screen-time
            requests and invokes registered callbacks.
        pending_requests: Latest pending request payloads (experimental mode).
    """

    def __init__(self, auth: Authenticator) -> None:
        """Initialize the client.

        Args:
            auth: Authenticated :class:`~pyfamilysafety.authenticator.Authenticator`
                session.
        """
        self._api: FamilySafetyAPI = FamilySafetyAPI(auth=auth)
        self.accounts: list[Account] = []
        self.experimental: bool = False
        self.pending_requests = []
        self._pending_request_callbacks = []

    def get_account(self, user_id: str) -> Account:
        """Return the account with the given member ID.

        Args:
            user_id: Microsoft family member ID from the roster.

        Returns:
            Matching :class:`~pyfamilysafety.account.Account`.

        Raises:
            IndexError: If no account matches ``user_id``.
        """
        return [x for x in self.accounts if x.user_id == user_id][0]

    def get_request(self, request_id: str) -> dict:
        """Return a single pending request by ID.

        Args:
            request_id: Pending request identifier from the API.

        Returns:
            Raw pending request dictionary.

        Raises:
            ValueError: If the request is not in :attr:`pending_requests`.
        """
        request = [x for x in self.pending_requests if x["id"] == request_id]
        if len(request) > 0:
            return request[0]
        raise ValueError("Pending request not found")

    def get_account_requests(self, user_id: str) -> list:
        """Return pending requests for a family member.

        Args:
            user_id: Member ID (``puid`` field on pending requests).

        Returns:
            List of pending request dictionaries for that member.
        """
        return [x for x in self.pending_requests if x["puid"] == user_id]

    def add_pending_request_callback(self, callback: Callable) -> None:
        """Register a callback invoked after pending requests are refreshed.

        Args:
            callback: Callable; may be sync or async.

        Raises:
            ValueError: If ``callback`` is not callable.
        """
        if not callable(callback):
            raise ValueError("Object must be callable.")
        if callback not in self._pending_request_callbacks:
            self._pending_request_callbacks.append(callback)

    def remove_pending_request_callback(self, callback: Callable) -> None:
        """Remove a pending request callback.

        Args:
            callback: Previously registered callable.

        Raises:
            ValueError: If ``callback`` is not callable.
        """
        if not callable(callback):
            raise ValueError("Object must be callable.")
        if callback in self._pending_request_callbacks:
            self._pending_request_callbacks.remove(callback)

    async def _get_pending_requests(self):
        """Returns pending requests on the account."""
        response = await self._api.send_request("get_pending_requests")
        self.pending_requests = response.get("json").get("pendingRequests", [])
        # restrict pending requests to only screentime, other types not supported yet
        self.pending_requests = [
            x for x in self.pending_requests if x["type"] == "DeviceScreenTime"]
        for cb in self._pending_request_callbacks:
            if is_awaitable(cb):
                await cb()
            else:
                cb()
        return self.pending_requests

    async def approve_pending_request(self, request_id: str, extension_time: int) -> bool:
        """Approve a pending screen-time request.

        Args:
            request_id: Pending request identifier.
            extension_time: Extra screen time to grant, in **seconds**.

        Returns:
            ``True`` if the API responded with HTTP 204.
        """
        extension_time = extension_time*100 # convert seconds to ms
        request = self.get_request(request_id)
        response = await self._api.async_process_pending_request(
            request,
            True,
            extension_time
        )

        await self._get_pending_requests()
        return response["status"] == 204

    async def deny_pending_request(self, request_id: str) -> bool:
        """Deny a pending screen-time request.

        Args:
            request_id: Pending request identifier.

        Returns:
            ``True`` if the API responded with HTTP 204.
        """
        request = self.get_request(request_id)
        response = await self._api.async_process_pending_request(
            request,
            False
        )
        await self._get_pending_requests()
        return response["status"] == 204

    async def update(self):
        """Refresh family roster and all account data.

        On the first call, loads the roster and creates :class:`Account`
        instances. On every call, runs :meth:`Account.update` for each member.
        When :attr:`experimental` is enabled, also refreshes pending requests.

        Raises:
            AggregatorException: Not raised directly; transient aggregator errors
                are logged and ignored so cached data remains available.
        """
        try:
            if len(self.accounts) == 0:
                data = await self._api.send_request("get_accounts")
                self.accounts = await Account.from_dict(
                    self._api,
                    data["json"],
                    self.experimental
                )
            coros = []
            if self.experimental:
                coros.append(self._get_pending_requests())
            for account in self.accounts:
                coros.append(account.update())
            await asyncio.gather(*coros)
        except AggregatorException:
            _LOGGER.warning("Aggregator exception occured, ignoring this update request.")
