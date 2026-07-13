"""Minimal CLI entrypoint for package install verification."""

from __future__ import annotations


def main() -> None:
    from runtime import __version__

    print(f"parallax {__version__}")


if __name__ == "__main__":
    main()
