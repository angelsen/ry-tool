#!/usr/bin/env python3
"""Get version and package info from uv."""
import json
import subprocess
import sys

def get_version_info():
    """Get current version and package info from uv."""
    result = subprocess.run(
        ["/usr/bin/uv", "version", "--output-format", "json"],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print(f"ERROR: Failed to get version info", file=sys.stderr)
        print(result.stderr, file=sys.stderr)
        sys.exit(1)
    
    return json.loads(result.stdout)

if __name__ == "__main__":
    info = get_version_info()
    
    # Output format: VERSION|PACKAGE_NAME
    print(f"{info['version']}|{info['package_name']}")