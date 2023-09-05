"""The core MSFT family safety API"""

import logging

from .api import FamilySafetyAPI
from .account import Account

class FamilySafety:
    """The core family safety module."""

    def __init__(self, api) -> None:
        self.api: FamilySafetyAPI = api
        self.accounts: list[Account] = None
        self.pending_requests = []

    @classmethod
    async def create(cls, token, use_refresh_token: bool=False) -> 'FamilySafety':
        """Create an instance of the family safety module."""
        self = cls(await FamilySafetyAPI.create(token, use_refresh_token))
        accounts = await self.api.send_request("get_accounts")
        self.accounts = await Account.from_dict(self.api, accounts.get("json"))
        await self._get_pending_requests()
        return self

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

    async def _get_pending_requests(self):
        """Returns pending requests on the account."""
        response = await self.api.send_request("get_pending_requests")
        self.pending_requests = response.get("json").get("pendingRequests", [])
        # restrict pending requests to only screentime, other types not supported yet
        self.pending_requests = [
            x for x in self.pending_requests if x["type"] == "DeviceScreenTime"]
        return self.pending_requests

    async def approve_pending_request(self, request_id, extension_time) -> bool:
        """Approves a pending request and grants an extension in seconds."""
        extension_time = extension_time*100 # convert seconds to ms
        request = self.get_request(request_id)
        response = await self.api.send_request(
            endpoint="approve_pending_request",
            body={
                "id": request.get("id"),
                "request": {
                    "appId": request.get("id"),
                    "extension": extension_time,
                    "isGlobal": True,
                    "lockTime": request.get("lockTime"),
                    "platform": request.get("platform"),
                    "requestedTime": request.get("requestedTime")
                },
                "type": request.get("type")
            },
            USER_ID=request["puid"]
        )

        await self._get_pending_requests()
        return response["status"] == 204

    async def deny_pending_request(self, request_id) -> bool:
        """Deny a pending request."""
        request = self.get_request(request_id)
        response = await self.api.send_request(
            endpoint="deny_pending_request",
            body={
                "id": request.get("id"),
                "request": {
                    "appId": request.get("id"),
                    "extension": 0,
                    "isGlobal": True,
                    "lockTime": request.get("lockTime"),
                    "platform": request.get("platform"),
                    "requestedTime": request.get("requestedTime")
                },
                "type": request.get("type")
            },
            USER_ID=request["puid"]
        )

        await self._get_pending_requests()
        return response["status"] == 204

    async def update(self):
        """Updates submodules"""
        await self._get_pending_requests()
        for account in self.accounts:
            await account.update()
