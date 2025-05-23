# pylint: disable=line-too-long
"""pyfamilysafety API request handler."""

import logging

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

    def __init__(self, auth: Authenticator) -> None:
        """Init API."""
        self._auth: Authenticator = auth
        self.pending_requests = []

    async def send_request(self, endpoint: str, body: object=None, headers: dict=None, platform: str=None, **kwargs):
        """Sends a request to a given endpoint."""
        _LOGGER.debug("Sending request to %s", endpoint)
        # Get the endpoint from the endpoints map
        e_point = ENDPOINTS.get(endpoint, None)
        if e_point is None:
            raise ValueError("Endpoint does not exist")
        # refresh the token if it has expired.
        if self._auth.access_token_expired:
            _LOGGER.debug("Token refresh required before continuing")
            await self._auth.perform_refresh()

        if headers is None:
            headers = {}
        headers["Authorization"] = self._auth.access_token
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
        async with self._auth.client_session.request(
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

    async def async_get_accounts(self):
        """Retrieve data from endpoint get_accounts."""
        return await self.send_request("get_accounts")

    async def async_get_pending_requests(self):
        """Retrieve data from endpoint get_pending_requests."""
        return await self.send_request("get_pending_requests")

    async def async_get_premium_entitlement(self):
        """Retrieve data from endpoint get_premium_entitlement."""
        return await self.send_request("get_premium_entitlement")

    async def async_get_user_app_screentime_usage(
            self,
            user_id,
            begin_time,
            end_time,
            platform
        ):
        """Retrieve data from endpoint get_user_app_screentime_usage."""
        return await self.send_request(
            "get_user_app_screentime_usage",
            headers={
                "Plat-Info": platform
            },
            USER_ID=user_id,
            BEGIN_TIME=begin_time,
            END_TIME=end_time
        )

    async def async_get_user_device_screentime_usage(
            self,
            user_id,
            begin_time,
            end_time,
            device_count,
            platform
        ):
        """Retrieve data from endpoint get_user_device_screentime_usage."""
        return await self.send_request(
            "get_user_device_screentime_usage",
            headers={
                "Plat-Info": platform
            },
            USER_ID=user_id,
            BEGIN_TIME=begin_time,
            END_TIME=end_time,
            DEVICE_COUNT=device_count,
        )

    async def async_get_user_devices(self, user_id):
        """Retrieve data from endpoint get_user_devices."""
        return await self.send_request("get_user_devices", USER_ID=user_id)

    async def async_get_user_spending(self, user_id):
        """Retrieve data from endpoint get_user_spending."""
        return await self.send_request("get_user_spending", USER_ID=user_id)

    async def async_get_user_payment_methods(self, user_id, cid):
        """Retrieve data from endpoint get_user_payment_methods."""
        return await self.send_request("get_user_payment_methods", USER_ID=user_id, CID=cid)

    async def async_get_user_content_restrictions(self, user_id):
        """Retrieve data from endpoint get_user_content_restrictions."""
        return await self.send_request("get_user_content_restrictions", USER_ID=user_id)

    async def async_get_override_device_restrictions(self, user_id):
        """Send a GET request to override device restrictions."""
        return await self.send_request("get_override_device_restrictions", USER_ID=user_id)

    async def async_process_pending_request(
            self,
            request: dict,
            approved: bool,
            extension_time: int=0
    ):
        """Process a pending request using the deny and approve pending request method"""
        if approved:
            return await self.async_approve_pending_request(
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
                user_id=request["puid"]
            )
        return await self.async_deny_pending_request(
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
            user_id=request["puid"]
        )

    async def async_deny_pending_request(self, user_id, body):
        """Send a POST request to deny a pending request."""
        return await self.send_request("deny_pending_request", USER_ID=user_id, body=body)

    async def async_approve_pending_request(self, user_id, body):
        """Send a POST request to approve a pending request."""
        return await self.send_request("approve_pending_request", USER_ID=user_id, body=body)

    async def async_override_device_restriction(self, user_id, body):
        """Send a POST request to override device restrictions."""
        return await self.send_request("override_device_restriction", USER_ID=user_id, body=body)
