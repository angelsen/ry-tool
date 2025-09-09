"""
Template processor for ry.
Handles {{var|default}} substitution in strings after YAML parsing.
"""

import re
import os
from typing import Any, Dict, List
from .exceptions import TemplateError


class TemplateProcessor:
    """Process template variables in strings with pipe defaults."""

    def __init__(self, args: List[str], metadata: Dict[str, str] = None):
        """Initialize with arguments, environment, and optional metadata."""
        self.context = self._build_context(args, metadata)

    def _build_context(self, args: List[str], metadata: Dict[str, str] = None) -> Dict[str, str]:
        """Build substitution context from args, environment, and metadata."""
        ctx = {}

        # Arguments
        for i, arg in enumerate(args):
            ctx[f"args.{i}"] = arg

        # Always provide these, even if empty
        ctx["args.all"] = " ".join(args) if args else ""
        ctx["args.first"] = args[0] if args else ""
        ctx["args.last"] = args[-1] if args else ""
        ctx["args.rest"] = " ".join(args[1:]) if len(args) > 1 else ""

        # Environment variables
        for key, value in os.environ.items():
            ctx[f"env.{key}"] = value

        # Add metadata (library info, etc.) if provided
        if metadata:
            ctx.update(metadata)

        return ctx

    def process(self, value: Any) -> Any:
        """Process any value, applying templates if needed."""
        if isinstance(value, str):
            return self._process_string(value)
        elif isinstance(value, dict):
            return {k: self.process(v) for k, v in value.items()}
        elif isinstance(value, list):
            return [self.process(item) for item in value]
        return value

    def _process_string(self, text: str) -> str:
        """Process {{var|default}} patterns in string."""
        if "{{" not in text:
            return text

        # Pattern matches {{...}} where ... doesn't contain }}
        pattern = r"\{\{([^}]+)\}\}"

        def replacer(match):
            expr = match.group(1)

            # Split by pipe - first part is variable, rest is default
            parts = expr.split("|", 1)  # Split only on first pipe
            var_name = parts[0].strip()

            # Check if variable exists in context
            if var_name in self.context:
                value = self.context[var_name]
                if value is not None:
                    return str(value)

            # Variable not found or None, check for default
            if len(parts) > 1:
                # Everything after the pipe is the explicit default
                return parts[1]  # Don't strip - preserve user's exact default

            # No default provided - fail
            raise TemplateError(f"Template variable '{var_name}' not found")

        return re.sub(pattern, replacer, text)
