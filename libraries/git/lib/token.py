#!/usr/bin/env python3
"""Shared token generation for git workflows."""

import hashlib
import subprocess
import time
import sys


def get_staged_hash() -> str:
    """Get hash of staged content."""
    try:
        result = subprocess.run(
            ["git", "diff", "--staged"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            return hashlib.sha256(result.stdout.encode()).hexdigest()[:8]
    except Exception:
        pass
    return ""


def generate_token(content_hash: str, window: int) -> str:
    """Generate token from content hash and time window."""
    token_input = f"{content_hash}:{window}"
    return hashlib.sha256(token_input.encode()).hexdigest()[:8]


def get_current_token() -> tuple[str, int]:
    """Get current token and seconds until expiry."""
    staged_hash = get_staged_hash()
    if not staged_hash:
        return "", 0
    
    timestamp = int(time.time())
    window = timestamp // 300  # 5-minute windows
    token = generate_token(staged_hash, window)
    expires_in = 300 - (timestamp % 300)
    
    return token, expires_in


def verify_token(provided_token: str) -> bool:
    """Verify if provided token matches current staged content."""
    staged_hash = get_staged_hash()
    if not staged_hash:
        return False
    
    timestamp = int(time.time())
    current_window = timestamp // 300
    
    # Check current window and previous window (in case we just crossed boundary)
    for window in [current_window, current_window - 1]:
        expected_token = generate_token(staged_hash, window)
        if provided_token == expected_token:
            return True
    
    return False


if __name__ == "__main__":
    # CLI usage
    if len(sys.argv) > 1:
        if sys.argv[1] == "generate":
            token, expires = get_current_token()
            if token:
                print(f"REVIEW_TOKEN={token}", file=sys.stderr)
                print(f"# Expires in {expires} seconds", file=sys.stderr)
        elif sys.argv[1] == "verify":
            if len(sys.argv) > 2:
                if verify_token(sys.argv[2]):
                    sys.exit(0)
            sys.exit(1)