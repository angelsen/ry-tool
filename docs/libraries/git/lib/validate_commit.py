#!/usr/bin/env python3
"""Validate conventional commit format."""

import re
from typing import Tuple


def validate_conventional(message: str) -> Tuple[bool, str | None]:
    """Validate conventional commit format.
    
    Returns: (is_valid, error_message)
    """
    lines = message.split("\n")
    header = lines[0]
    
    # Valid types
    valid_types = ["feat", "fix", "docs", "style", "refactor", "test", "chore", "perf", "ci", "build", "revert"]
    
    # Check format: type(scope): description or type: description
    pattern = r"^(" + "|".join(valid_types) + r")(\([^)]+\))?(!)?:\s+(.+)"
    match = re.match(pattern, header)
    
    if not match:
        # Check for common mistakes
        if ":" not in header:
            return False, "missing colon - use 'type: description'"
        
        first_word = header.split(":")[0].split("(")[0].lower()
        
        # Common typos
        typos = {
            "feature": "feat",
            "bugfix": "fix", 
            "bug": "fix",
            "doc": "docs",
            "tests": "test",
        }
        
        if first_word in typos:
            return False, f"use '{typos[first_word]}' instead of '{first_word}'"
        
        if first_word not in valid_types:
            return False, f"invalid type '{first_word}' - valid: {', '.join(valid_types)}"
        
        return False, "invalid format - use 'type: description' or 'type(scope): description'"
    
    _, _, breaking, description = match.groups()
    
    # Check description quality
    if len(description) < 10:
        return False, "description too short (min 10 chars)"
    
    if description[0].isupper():
        return False, "description should start lowercase"
    
    if description.endswith("."):
        return False, "description should not end with period"
    
    return True, None


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        msg = sys.argv[1]
        valid, error = validate_conventional(msg)
        if not valid:
            print(f"ERROR: {error}", file=sys.stderr)
            sys.exit(1)
        print("OK", file=sys.stderr)
        sys.exit(0)