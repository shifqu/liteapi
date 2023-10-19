"""HTTP server models."""
from dataclasses import dataclass, field
from typing import Any

ListStr = list[str]


def _default_response_headers():
    return {"Access-Control-Allow-Origin": "*"}


@dataclass
class Request:
    """Represent a Request."""

    method: str
    headers: dict[str, str]
    path: str
    query_params: dict[str, ListStr] = field(default_factory=dict)
    body: str = ""


@dataclass
class Response:
    """Represent a Response."""

    body: Any
    status_code: int = 200
    content_type: str = "text/html"
    headers: dict[str, str] = field(default_factory=_default_response_headers)


@dataclass
class JSONResponse(Response):
    """Represent a JSON Response."""

    content_type: str = "application/json"
