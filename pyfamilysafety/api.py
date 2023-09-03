"""pyfamilysafety API request handler."""

import logging
from datetime import datetime

import aiohttp

from .authenticator import Authenticator
from .const import ENDPOINTS, BASE_URL
from .exceptions import HttpException

_LOGGER = logging.getLogger(__name__)

def _check_http_success(status: int) -> bool:
    return status >= 200 and status < 300

class FamilySafetyAPI:
    """The API."""

    def __init__(self) -> None:
        """Init API."""
        self.authenticator: Authenticator = None

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

    async def send_request(self, endpoint: str, body: object=None, **kwargs):
        """Sends a request to a given endpoint."""
        _LOGGER.debug("Sending request to %s", endpoint)
        # Get the endpoint from the endpoints map
        e_point = ENDPOINTS.get(endpoint, None)
        if e_point is None:
            raise ValueError("Endpoint does not exist")
        # refresh the token if it has expired.
        if self.authenticator.expires < datetime.now():
            await self.authenticator.refresh_token()
        # format the URL using the kwargs
        url = e_point.get("url").format(BASE_URL=BASE_URL, **kwargs)
        _LOGGER.debug("Built URL %s", url)
        # now send the HTTP request
        resp: dict = {
            "status": 0,
            "text": "",
            "json": "",
            "headers": ""
        }
        async with aiohttp.ClientSession() as session:
            # Add auth header
            session.headers.add("Authorization", self._auth_token)
            async with session.request(
                method=e_point.get("method"),
                url=url,
                json=body
            ) as response:
                _LOGGER.debug("Request to %s status code %s", url, response.status)
                if _check_http_success(response.status):
                    resp["status"] = response.status
                    resp["text"] = await response.text()
                    resp["json"] = await response.json()
                    resp["headers"] = response.headers
                else:
                    raise HttpException("HTTP Error", response.status)

        # now return the resp dict
        return resp
