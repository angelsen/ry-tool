#!/usr/bin/env python3
"""
ry - Run YAML orchestration
A minimal, composable command orchestrator.
"""
import sys
from .core import RY

def main():
    """Main entry point for ry."""
    try:
        ry = RY()
        sys.exit(ry.run())
    except KeyboardInterrupt:
        sys.exit(130)
    except Exception as e:
        print(f"FAIL: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()