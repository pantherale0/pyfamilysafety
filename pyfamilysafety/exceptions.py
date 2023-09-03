"""pyfamilysafety exceptions"""

class HttpException(Exception):
    """A HTTP excepton."""

    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class Unauthorized(HttpException):
    """An unauthorized error."""

    def __init__(self) -> None:
        super().__init__("HTTP Unauthorized")

class RequestDenied(HttpException):
    """An access denied error."""

    def __init__(self, message="HTTP Access Denied") -> None:
        super().__init__(message)
