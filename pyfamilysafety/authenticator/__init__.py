# pylint: disable=line-too-long
"""Microsoft authentication handler."""

import logging
import asyncio
from datetime import datetime, timedelta

from urllib.parse import urlparse

import aiohttp
from pyfamilysafety.exceptions import Unauthorized

from .const import (
    TOKEN_ENDPOINT,
    USER_AGENT,
    REDIRECT_URL,
    CLIENT_ID,
    SCOPE
)

_LOGGER = logging.getLogger(__name__)

class Authenticator:
    """The base authenticator class."""

    def __init__(
            self,
            client_session: aiohttp.ClientSession = None
        ) -> None:
        """init the class."""
        _LOGGER.debug(">> Init authenticator.")
        self.expires: datetime = None
        self.refresh_token: str = None
        self._access_token: str = None
        self.user_id: str = None
        self._ppft: str = None
        self._login_lock: asyncio.Lock = asyncio.Lock()
        if client_session is None:
            client_session = aiohttp.ClientSession()
        self.client_session: aiohttp.ClientSession = client_session

    @property
    def access_token(self) -> str:
        """Returns the access token."""
        return f"MSAuth1.0 usertoken=\"{self._access_token}\", type=\"MSACT\""

    @property
    def access_token_expired(self) -> bool:
        """Check if the access token has expired."""
        return self.expires < (datetime.now()+timedelta(minutes=1))

    @classmethod
    async def create(
        cls,
        token: str,
        use_refresh_token: bool=False,
        client_session: aiohttp.ClientSession | None = None) -> 'Authenticator':
        """Creates and starts a Microsoft auth session without retaining the username and password."""
        auth = cls(client_session=client_session)
        if use_refresh_token:
            auth.refresh_token = token
            await auth.perform_refresh()
            return auth
        else:
            redir_parsed = auth._parse_response_token(token)
            await auth.perform_login(redir_parsed["code"])
            return auth

    def _parse_response_token(self, redirect_url: str) -> dict:
        """Parses a redirect_url."""
        _LOGGER.debug(">> Parsing redirect_url.")
        try:
            url = urlparse(redirect_url)
            params = url.query.split('&')
            response = {}
            for param in params:
                response = {
                    **response,
                    param.split('=')[0]: param.split('=')[1]
                }
            return response
        except Exception as exc:
            raise ValueError("Invalid URL provided.") from exc

    async def _request_handler(self, method, url, body=None, headers=None, data=None):
        """Send a HTTP request"""
        response: dict = {
            "status": 0,
            "text": "",
            "json": "",
            "headers": ""
        }
        if not headers:
            headers = {}
        headers = {
            **headers,
            "user-agent": USER_AGENT,
            "X-Requested-With": "com.microsoft.familysafety"
        }
        async with self.client_session.request(
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
                await asyncio.sleep(2)
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
                self._access_token = tokens["json"]["access_token"]
                self.expires = datetime.now() + timedelta(seconds=tokens["json"]["expires_in"])
                self.refresh_token = tokens["json"]["refresh_token"]
                self.user_id = tokens["json"]["user_id"]
            else:
                raise Unauthorized()

    async def perform_refresh(self):
        """Refresh the token."""
        if self._login_lock.locked():
            while self._login_lock.locked():
                await asyncio.sleep(2)
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
                self._access_token = tokens["json"]["access_token"]
                self.expires = datetime.now() + timedelta(seconds=tokens["json"]["expires_in"])
                self.refresh_token = tokens["json"]["refresh_token"]
                self.user_id = tokens["json"]["user_id"]
