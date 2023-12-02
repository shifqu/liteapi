"""HTTP server errors."""
from liteapi.models import JSONResponse


class ApiException(JSONResponse, BaseException):
    """Raised whenever an exception occurred during request/response handling."""

    def __str__(self) -> str:
        """Return only the exception message as a str representation."""
        return self.body["message"]
