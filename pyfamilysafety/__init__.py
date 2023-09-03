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
        return self

    def get_account(self, user_id) -> Account:
        """Returns an account for the given ID."""
        return [x for x in self.accounts if x.user_id == user_id][0]

    async def get_pending_requests(self):
        """Returns pending requests on the account."""
        response = await self.api.send_request("get_pending_requests")
        self.pending_requests = response.get("json")
        return self.pending_requests

    async def update(self):
        """Updates submodules"""
        await self.get_pending_requests()
        for account in self.accounts:
            await account.update()
