# pylint: disable=line-too-long
"""Microsoft authentication handler."""

import logging
import re
import asyncio
from datetime import datetime, timedelta

import aiohttp
from pyfamilysafety.exceptions import Unauthorized

from .const import (
    TOKEN_ENDPOINT,
    USER_AGENT,
    REDIRECT_URL,
    REDIR_REGEXP,
    CLIENT_ID,
    SCOPE
)

_LOGGER = logging.getLogger(__name__)

def _parse_redirect_url(redirect_url: str) -> dict:
    """Parses the received redirect token."""
    matches = re.findall(REDIR_REGEXP, redirect_url)
    if len(matches) == 1:
        return {
            "code": matches[0][0],
            "lc": matches[0][1]
        }
    else:
        raise ValueError("Invalid redirect_url provided.")

class Authenticator:
    """The base authenticator class."""

    def __init__(self) -> None:
        """init the class."""
        _LOGGER.debug(">> Init authenticator.")
        self.expires: datetime = None
        self.refresh_token: str = None
        self.access_token: str = None
        self.user_id: str = None
        self._ppft: str = None
        self._login_lock: asyncio.Lock = asyncio.Lock()

    @classmethod
    async def create(cls, token: str, use_refresh_token: bool=False) -> 'Authenticator':
        """Creates and starts a Microsoft auth session without retaining the username and password."""
        auth = cls()
        if use_refresh_token:
            auth.refresh_token = token
            await auth.perform_refresh()
            return auth
        else:
            redir_parsed = _parse_redirect_url(token)
            await auth.perform_login(redir_parsed["code"])
            return auth

    async def _request_handler(self, method, url, body=None, headers=None, data=None):
        """Send a HTTP request"""
        response: dict = {
            "status": 0,
            "text": "",
            "json": "",
            "headers": ""
        }
        async with aiohttp.ClientSession() as session:
            session.headers.add("user-agent", USER_AGENT)
            session.headers.add("X-Requested-With", "com.microsoft.familysafety")
            if headers:
                for k in headers:
                    session.headers.add(k, headers[k])
            async with session.request(
                method=method,
                url=url,
                json=body,
                headers=headers,
                data=data
            ) as resp:
                response["status"] = resp.status
                response["text"] = await resp.text()
                response["json"] = await resp.json()
                response["headers"] = resp.headers
        return response

    async def perform_login(self, auth_code):
        """Performs login from the username and password."""
        if self._login_lock.locked():
            while self._login_lock.locked():
                asyncio.sleep(2)
            return
        async with self._login_lock:
            _LOGGER.debug(">> Performing authenticator login")
            form = aiohttp.FormData()
            form.add_field("client_id", CLIENT_ID)
            form.add_field("code", auth_code)
            form.add_field("grant_type", "authorization_code")
            form.add_field("redirect_uri", REDIRECT_URL)
            form.add_field("scope", SCOPE)
            tokens = await self._request_handler(
                method="POST",
                url=TOKEN_ENDPOINT,
                data=form
            )
            _LOGGER.debug(">> Token request response %s", tokens["status"])
            if tokens["status"] == 200:
                self.access_token = tokens["json"]["access_token"]
                self.expires = datetime.now() + timedelta(seconds=tokens["json"]["expires_in"])
                self.refresh_token = tokens["json"]["refresh_token"]
                self.user_id = tokens["json"]["user_id"]
            else:
                raise Unauthorized()

    async def perform_refresh(self):
        """Refresh the token."""
        if self._login_lock.locked():
            while self._login_lock.locked():
                asyncio.sleep(2)
            return
        async with self._login_lock:
            _LOGGER.debug(">> Performing authenticator refresh")
            form = aiohttp.FormData()
            form.add_field("client_id", CLIENT_ID)
            form.add_field("refresh_token", self.refresh_token)
            form.add_field("grant_type", "refresh_token")
            form.add_field("scope", SCOPE)
            tokens = await self._request_handler(
                method="POST",
                url=TOKEN_ENDPOINT,
                data=form
            )
            _LOGGER.debug(">> Token request response %s", tokens["status"])
            _LOGGER.debug(">> Token response value %s", tokens)
            if tokens["status"] == 200:
                self.access_token = tokens["json"]["access_token"]
                self.expires = datetime.now() + timedelta(seconds=tokens["json"]["expires_in"])
                self.refresh_token = tokens["json"]["refresh_token"]
                self.user_id = tokens["json"]["user_id"]
