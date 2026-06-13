"""pyfamilysafety exceptions"""

class HttpException(Exception):
    """Base exception for HTTP errors from the Family Safety API.

    Raised by :meth:`pyfamilysafety.api.FamilySafetyAPI.send_request` for
    non-success status codes not mapped to a specific subclass.
    """

    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class Unauthorized(HttpException):
    """HTTP 401 or failed token exchange.

    Raised when authentication fails during login, refresh, or API calls.
    """

    def __init__(self) -> None:
        super().__init__("HTTP Unauthorized")

class RequestDenied(HttpException):
    """HTTP 403 access denied.

    Raised when the authenticated user lacks permission for the requested action.
    """

    def __init__(self, message="HTTP Access Denied") -> None:
        super().__init__(message)

class AggregatorException(HttpException):
    """Transient Microsoft aggregator failure (HTTP 500).

    Raised when the response body contains the known aggregator error message.
    :meth:`pyfamilysafety.FamilySafety.update` catches this and skips the refresh.
    """

    def __init__(self) -> None:
        super().__init__("An upstream aggregator error occured.")
