"""HTTP server configuration."""
import os
from dataclasses import dataclass
from distutils.util import strtobool
from typing import Literal


@dataclass
class ServerConfig:
    """Represent the configuration for the HTTP server."""

    write_to_file: Literal[0, 1] = 0


def server_config() -> ServerConfig:
    """Attempt to get the config's fields from the environment."""
    try:
        write_to_file = strtobool(os.environ["WRITE_TO_FILE"])
    except KeyError:
        return ServerConfig()
    except ValueError as exc:
        raise Exception(f"Please export {exc} as a boolean environment variable.")

    return ServerConfig(write_to_file=write_to_file)
