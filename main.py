"""HTTP server main functionality."""
import logging
import re
import signal
import socketserver
import traceback
from datetime import datetime, timezone
from pathlib import Path
from socket import SHUT_WR, socket
from typing import Callable, NoReturn

from liteapi.config import server_config
from liteapi.errors import ApiException
from liteapi.utils import build_response, parse_request

Route = tuple[re.Pattern, Callable]

SERVER_CONFIG = server_config()


class ApplicationServer(socketserver.TCPServer):
    """Represent a TCPServer that supports routes and whose address can be reused."""

    allow_reuse_address = True

    def __init__(self, *args, routes: list[Route] | None = None, **kwargs) -> None:
        self.routes = routes or []
        super().__init__(*args, **kwargs)


class TCPHandler(socketserver.BaseRequestHandler):
    """Represent a TCPHandler which handles request and ensures the tcp_socket is shutdown."""

    def handle(self) -> None:
        """Handle the tcp request."""
        tcp_socket: socket = self.request
        request_str = tcp_socket.recv(4096).decode()
        self._write_to_file(request_str, "request")
        try:
            request = parse_request(request_str)
            route_function = self._get_route_function(request.path)
            response = route_function(request)
        except ApiException as exc:
            response = exc
        except Exception:
            print(traceback.format_exc())
            response = ApiException({"ok": False}, 500)
        response_str = build_response(response)
        self._write_to_file(response_str, "response")
        response_bytes = response_str.encode()
        tcp_socket.sendall(response_bytes)

    def finish(self) -> None:
        """Try to shutdown the tcp_socket in a safe way."""
        tcp_socket: socket = self.request
        try:
            tcp_socket.shutdown(SHUT_WR)
        except OSError:
            """Happens when the transport endpoint is not connected."""

    def _get_route_function(self, searched_path: str) -> Callable:
        """Get the route fuction for the searched_path.

        This function only works for ApplicationServer instances.
        A default 404 is returned when no route matches searched_path.
        If you would like to override the default 404, define a route with a wildcard route_path
        e.g.::

            @app.route("/.*")
            def fallback_route(request):
                raise ApiException({"ok": False, "error": "Custom 404!"}, status_code=404)

        IMPORTANT: The routes are added by-occurrence, so make sure to define the wildcard
        route_path as the last route, any routes added later will not be available.

        Parameters
        ----------
        searched_path : str
            The route that the user attempted to visit.

        Returns
        -------
        Callable
            The callable corresponding to the visited route.

        Raises
        ------
        ApiException
            In case no route was found.
        """
        assert isinstance(self.server, ApplicationServer), f"{type(self.server)} is not supported."
        route = next((route for route in self.server.routes if route[0].match(searched_path)), None)
        if route is None:
            raise ApiException({"ok": False}, status_code=404)
        return route[1]

    @staticmethod
    def _write_to_file(text: str, name: str) -> None:
        if not SERVER_CONFIG.write_to_file:
            return
        now_timestamp = int(datetime.now(tz=timezone.utc).timestamp())
        root = Path(__file__).parent.parent.parent
        destination_dir = root / "tests" / "data" / "server" / str(now_timestamp)
        destination_dir.mkdir(exist_ok=True, parents=True)
        filepath = destination_dir / f"{name}.txt"
        filepath.write_text(text, newline="\n")


class Application:
    """Represent the main Application."""

    routes: list[Route] = []

    def __init__(self):
        """Shutdown on SIGTERM signal."""
        signal.signal(signal.SIGTERM, self.shutdown)

    def route(self, path: str) -> Callable:
        """Register the given path as a route.

        The decorated function is executed it once a request on the given path is received.

        Parameters
        ----------
        path : str
            The path to be added as a route.
        """

        def _decorator(func: Callable):
            def _inner():
                return func()

            self.routes.append((re.compile(path + "$"), func))
            return _inner

        return _decorator

    def serve(self, host: str, port: int):
        """Activate the server.

        This will keep running until you interrupt the program with Ctrl-C.
        The SIGTERM signal will also interrupt the program.

        Parameters
        ----------
        host : str
            The host on which we will listen for requests.
        port : int
            The port on which we will listen for requests.
        """
        logging.info(f"Serving on {host}:{port}")
        with ApplicationServer((host, port), TCPHandler, routes=self.routes) as server:
            server.serve_forever()

    @staticmethod
    def shutdown(*_) -> NoReturn:
        """Shutdown by raising a KeyboardInterrupt."""
        raise KeyboardInterrupt()
