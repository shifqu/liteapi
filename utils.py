"""HTTP server utils."""
import json
from urllib.parse import parse_qs, urlparse

from liteapi.models import Request, Response


def build_response(response: Response) -> str:
    """Build a string response from the given Response object."""
    headers = _build_headers_str(response)
    body = _build_body_str(response)
    response_str = _build_response_str(response, headers, body)
    return response_str


def parse_request(request_str: str) -> Request:
    """Parse the given request string to a Request object."""
    request_lines = request_str.splitlines()
    if not request_lines:
        raise TypeError("Malformed request.")  # This is likely a connect attempt
    method, url_str, _ = request_lines[0].split(" ")
    empty_line_index = request_lines.index("")  # Everything below the first empty line is body
    headers = _parse_headers(request_lines, empty_line_index)
    body = _parse_body(request_lines, empty_line_index)
    url = urlparse(url_str)
    return Request(method, headers, url.path, parse_qs(url.query), body)


def _build_body_str(response: Response) -> str:
    if isinstance(response.body, str):
        return response.body
    return json.dumps(response.body)


def _build_headers_str(response: Response) -> str:
    headers = "\n".join(f"{key}: {value}" for key, value in response.headers.items())
    if headers:
        headers += "\n"  # Append a new-line in case additional headers are present.
    return headers


def _build_response_str(response: Response, headers: str, body: str) -> str:
    return (
        f"HTTP/1.1 {response.status_code}\n"
        f"Content-Type: {response.content_type}; charset=utf-8\n"
        f"Content-Length: {len(body)}\n"
        "Connection: close\n"
        f"{headers}"
        f"\n"
        f"{body}"
    )


def _parse_body(request_lines: list[str], empty_line_index: int) -> str:
    body_lines = request_lines[empty_line_index + 1 :]
    return "".join(body_lines)


def _parse_headers(request_lines: list[str], empty_line_index: int) -> dict[str, str]:
    headers = {}
    for line in request_lines[1:empty_line_index]:
        key, value = (part.strip() for part in line.split(":", 1))
        uppercase_key = key.upper()
        headers[uppercase_key] = value
    return headers
