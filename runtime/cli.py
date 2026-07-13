"""Minimal CLI entrypoint for package install verification."""

from __future__ import annotations


def main() -> None:
    from runtime import __version__

    print(f"reliable-agent-systems {__version__}")


if __name__ == "__main__":
    main()
