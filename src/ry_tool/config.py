"""
Central configuration for ry.
Provides paths to interpreters and system binaries.
"""

import os


class Config:
    """Central configuration for all system paths and URLs."""

    # Binary paths - can be overridden via environment variables
    PYTHON = os.environ.get("RY_PYTHON", "/usr/bin/python3")
    SHELL = os.environ.get("RY_SHELL", "/bin/sh")
    BASH = os.environ.get("RY_BASH", "/bin/bash")
    GIT = os.environ.get("RY_GIT", "/usr/bin/git")
    BASE64 = os.environ.get("RY_BASE64", "base64")
    CURL = os.environ.get("RY_CURL", "curl")

    # Registry URL - can be overridden via environment
    REGISTRY_URL = os.environ.get(
        "RY_REGISTRY_URL", "https://angelsen.github.io/ry-tool"
    )


# Global config instance for convenience
config = Config()
