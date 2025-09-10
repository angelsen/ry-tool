#!/usr/bin/env python3
"""Commit message validation and cleaning."""

import re
import sys


def strip_ai_signatures(message: str) -> str:
    """
    Remove AI-generated signatures from commit messages.
    
    Args:
        message: Original commit message
    
    Returns:
        Cleaned message
    """
    # Common AI signatures to remove
    signatures = [
        r'[🤖\U0001F916].*$',  # Robot emoji lines
        r'Generated with \[Claude.*\].*$',
        r'Co-Authored-By: Claude.*$',
        r'Assistant:.*$',
        r'AI-Generated.*$',
    ]
    
    lines = message.split('\n')
    cleaned_lines = []
    
    for line in lines:
        # Check if line matches any signature pattern
        is_signature = False
        for pattern in signatures:
            if re.search(pattern, line, re.IGNORECASE | re.MULTILINE):
                is_signature = True
                break
        
        if not is_signature:
            cleaned_lines.append(line)
    
    # Remove trailing empty lines
    while cleaned_lines and not cleaned_lines[-1].strip():
        cleaned_lines.pop()
    
    return '\n'.join(cleaned_lines)


def validate_conventional_commit(message: str) -> tuple[bool, str]:
    """
    Validate if message follows conventional commit format.
    
    Args:
        message: Commit message to validate
    
    Returns:
        (is_valid, error_message)
    """
    # Conventional commit pattern
    # type(scope): description
    # 
    # body
    # 
    # footer
    
    lines = message.strip().split('\n')
    if not lines:
        return False, "Empty commit message"
    
    first_line = lines[0]
    
    # Valid types
    valid_types = [
        'feat', 'fix', 'docs', 'style', 'refactor',
        'perf', 'test', 'build', 'ci', 'chore', 'revert'
    ]
    
    # Check format: type(scope): description or type: description
    pattern = r'^(' + '|'.join(valid_types) + r')(\([^)]+\))?: .+$'
    
    if not re.match(pattern, first_line):
        return False, (
            f"First line must follow format: type(scope): description\n"
            f"  Valid types: {', '.join(valid_types)}\n"
            f"  Got: {first_line}"
        )
    
    # Check first line length (should be <= 72 chars)
    if len(first_line) > 72:
        return False, f"First line too long ({len(first_line)} > 72 chars)"
    
    # Check for lowercase type
    type_part = first_line.split(':')[0].split('(')[0]
    if type_part != type_part.lower():
        return False, f"Type must be lowercase: {type_part}"
    
    return True, ""


def process_commit_message(message: str) -> tuple[str, list[str]]:
    """
    Process commit message: clean and validate.
    
    Args:
        message: Original message
    
    Returns:
        (processed_message, warnings)
    """
    warnings = []
    
    # Strip AI signatures
    cleaned = strip_ai_signatures(message)
    if cleaned != message:
        warnings.append("Removed AI signatures from commit message")
    
    # Validate conventional commit
    is_valid, error = validate_conventional_commit(cleaned)
    if not is_valid:
        # Don't modify, just warn
        warnings.append(f"Non-conventional format: {error}")
    
    return cleaned, warnings


if __name__ == "__main__":
    # Test validation
    test_messages = [
        "feat: add new feature",
        "fix(api): handle null response",
        "This is not conventional",
        "feat: add feature\n\n🤖 Generated with Claude",
    ]
    
    for msg in test_messages:
        cleaned, warnings = process_commit_message(msg)
        print(f"INFO: Original: {msg[:50]}...", file=sys.stderr)
        print(f"INFO: Cleaned: {cleaned[:50]}...", file=sys.stderr)
        if warnings:
            print(f"WARNING: {warnings}", file=sys.stderr)