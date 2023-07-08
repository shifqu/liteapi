"""HTTP server errors."""
from liteapi.models import JSONResponse


class ApiException(JSONResponse, BaseException):
    """Raised whenever an exception occurred during request/response handling."""
