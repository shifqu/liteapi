"""HTTP server models."""
from dataclasses import dataclass, field
from typing import Any

ListStr = list[str]


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
    headers: dict[str, str] = field(default_factory=dict)


@dataclass
class JSONResponse(Response):
    """Represent a JSON Response."""

    content_type: str = "application/json"
