"""Launcher: `python -m expense_tracker [--port N]`."""

import argparse

from expense_tracker.app import create_app

HOST = "127.0.0.1"  # Local-only by design (REQ-NFR-001); not configurable.
DEFAULT_PORT = 5000


def parse_port(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="expense_tracker")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    port = parser.parse_args(argv).port
    if not 1 <= port <= 65535:
        parser.error("port must be between 1 and 65535")
    return port


def main(argv: list[str] | None = None) -> None:
    create_app().run(host=HOST, port=parse_port(argv), debug=False)


if __name__ == "__main__":
    main()
