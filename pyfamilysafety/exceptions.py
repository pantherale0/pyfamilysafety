"""pyfamilysafety exceptions"""

class Unauthorized(Exception):
    """An unauthorized error."""

    def __init__(self) -> None:
        super().__init__("HTTP Unauthorized")

class RequestDenied(Exception):
    """An access denied error."""

    def __init__(self, message="HTTP Access Denied") -> None:
        super().__init__(message)
