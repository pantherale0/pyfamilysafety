# pylint: disable=line-too-long
"""pyfamilysafety API request handler."""

import logging
from datetime import datetime

import aiohttp
import aiohttp.client_exceptions

from .authenticator import Authenticator
from .const import ENDPOINTS, BASE_URL, AGGREGATOR_ERROR, USER_AGENT
from .exceptions import HttpException, AggregatorException, Unauthorized, RequestDenied

_LOGGER = logging.getLogger(__name__)

def _check_http_success(status: int) -> bool:
    return status >= 200 and status < 300

class FamilySafetyAPI:
    """The API."""

    def __init__(self) -> None:
        """Init API."""
        self.authenticator: Authenticator = None
        self._session: aiohttp.ClientSession = aiohttp.ClientSession()

    @classmethod
    async def create(cls, token: str, use_refresh_token: bool=False) -> 'FamilySafetyAPI':
        """Create an instance of the base API handler library."""
        self = cls()
        self.authenticator = await Authenticator.create(token, use_refresh_token)
        return self

    @property
    def _auth_token(self) -> str:
        """Returns the auth token."""
        return f"MSAuth1.0 usertoken=\"{self.authenticator.access_token}\", type=\"MSACT\""

    async def end_session(self):
        """Ends the active session, this method should be called before GC."""
        await self._session.close()

    async def send_request(self, endpoint: str, body: object=None, headers: dict=None, platform: str=None, **kwargs):
        """Sends a request to a given endpoint."""
        _LOGGER.debug("Sending request to %s", endpoint)
        # Get the endpoint from the endpoints map
        e_point = ENDPOINTS.get(endpoint, None)
        if e_point is None:
            raise ValueError("Endpoint does not exist")
        # refresh the token if it has expired.
        if self.authenticator.expires is not None:
            if self.authenticator.expires < datetime.now():
                _LOGGER.debug("Token refresh required before continuing")
                await self.authenticator.perform_refresh()
                self._session.headers.pop("Authorization")

        if self.authenticator.expires is None:
            _LOGGER.warning("Missing expiration of access token in authenticator, attempting to refresh anyway.")
            await self.authenticator.perform_refresh()
            try:
                self._session.headers.pop("Authorization")
            except KeyError:
                pass

        if self._session.headers.get("Authorization", None) is None:
            # Add the auth token
            self._session.headers.add("Authorization", self._auth_token)
        # add headers to override
        if headers is None:
            headers = {}
            headers["Authorization"] = self._auth_token
            headers["User-Agent"] = USER_AGENT
            headers["Content-Type"] = "application/json"
        if platform is not None:
            headers["Plat-Info"] = platform

        # format the URL using the kwargs
        url = e_point.get("url")
        if "{BASE_URL" in url:
            url = url.format(BASE_URL=BASE_URL, **kwargs)
        else:
            url = url.format(**kwargs)
        _LOGGER.debug("Built URL %s", url)
        # now send the HTTP request
        resp: dict = {
            "status": 0,
            "text": "",
            "json": "",
            "headers": ""
        }
        async with self._session.request(
            method=e_point.get("method"),
            url=url,
            json=body,
            headers=headers
        ) as response:
            _LOGGER.debug("Request to %s status code %s", url, response.status)
            if _check_http_success(response.status):
                resp["status"] = response.status
                if response.status != 204:
                    resp["text"] = await response.text()
                    try:
                        resp["json"] = await response.json()
                    except aiohttp.client_exceptions.ContentTypeError:
                        _LOGGER.debug("Unable to parse JSON response - invalid content type.")
                resp["headers"] = response.headers
            else:
                text = await response.text()
                if response.status == 500 and AGGREGATOR_ERROR in text:
                    raise AggregatorException()
                if response.status == 401:
                    raise Unauthorized()
                if response.status == 403:
                    raise RequestDenied(await response.text())

                raise HttpException("HTTP Error", response.status, await response.text())

        # now return the resp dict
        return resp
