"""The core MSFT family safety API"""

import asyncio
import logging

from .authenticator import Authenticator
from .api import FamilySafetyAPI
from .account import Account
from .exceptions import AggregatorException
from .utils import is_awaitable

_LOGGER = logging.getLogger(__name__)

class FamilySafety:
    """The core family safety module."""

    def __init__(self, auth: Authenticator) -> None:
        """Initialize the family safety module."""
        self._api: FamilySafetyAPI = FamilySafetyAPI(auth=auth)
        self.accounts: list[Account] = []
        self.experimental: bool = False
        self.pending_requests = []
        self._pending_request_callbacks = []

    def get_account(self, user_id) -> Account:
        """Returns an account for the given ID."""
        return [x for x in self.accounts if x.user_id == user_id][0]

    def get_request(self, request_id) -> dict:
        """Returns a single pending request."""
        request = [x for x in self.pending_requests if x["id"] == request_id]
        if len(request) > 0:
            return request[0]
        raise ValueError("Pending request not found")

    def get_account_requests(self, user_id) -> list:
        """Returns all pending requests for a given account."""
        return [x for x in self.pending_requests if x["puid"] == user_id]

    def add_pending_request_callback(self, callback):
        """Add a callback to the pending request."""
        if not callable(callback):
            raise ValueError("Object must be callable.")
        if callback not in self._pending_request_callbacks:
            self._pending_request_callbacks.append(callback)

    def remove_pending_request_callback(self, callback):
        """Remove a given pending request callback."""
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

    async def approve_pending_request(self, request_id, extension_time) -> bool:
        """Approves a pending request and grants an extension in seconds."""
        extension_time = extension_time*100 # convert seconds to ms
        request = self.get_request(request_id)
        response = await self._api.async_process_pending_request(
            request,
            True,
            extension_time
        )

        await self._get_pending_requests()
        return response["status"] == 204

    async def deny_pending_request(self, request_id) -> bool:
        """Deny a pending request."""
        request = self.get_request(request_id)
        response = await self._api.async_process_pending_request(
            request,
            False
        )
        await self._get_pending_requests()
        return response["status"] == 204

    async def update(self):
        """Updates submodules"""
        try:
            if len(self.accounts) == 0:
                data = await self._api.send_request("get_accounts")
                self.accounts = await Account.from_dict(
                    self._api,
                    data,
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
