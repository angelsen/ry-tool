#!/usr/bin/env python3
"""
ry - Run YAML orchestration
Entry point for the ry command-line tool.
"""

from .app import run


def main():
    """Main entry point for ry."""
    run()


if __name__ == "__main__":
    main()
