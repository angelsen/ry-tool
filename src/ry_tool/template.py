"""
Template processor for ry.
Handles {{var|default}} substitution in strings after YAML parsing.
"""
import re
import os
import sys
from typing import Any, Dict, List


class TemplateProcessor:
    """Process template variables in strings with pipe defaults."""
    
    def __init__(self, args: List[str]):
        """Initialize with arguments and environment."""
        self.context = self._build_context(args)
    
    def _build_context(self, args: List[str]) -> Dict[str, str]:
        """Build substitution context from args and environment."""
        ctx = {}
        
        # Arguments
        for i, arg in enumerate(args):
            ctx[f'args.{i}'] = arg
        
        if args:
            ctx['args.all'] = ' '.join(args)
            ctx['args.first'] = args[0]
            ctx['args.last'] = args[-1]
            if len(args) > 1:
                ctx['args.rest'] = ' '.join(args[1:])
        
        # Environment variables
        for key, value in os.environ.items():
            ctx[f'env.{key}'] = value
        
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
        if '{{' not in text:
            return text
        
        # Pattern matches {{...}} where ... doesn't contain }}
        pattern = r'\{\{([^}]+)\}\}'
        
        def replacer(match):
            expr = match.group(1)
            
            # Split by pipe for defaults
            for part in expr.split('|'):
                part = part.strip()
                
                # Check context
                if part in self.context:
                    value = self.context[part]
                    if value is not None:
                        return str(value)
                
                # Not in context, treat as literal default
                elif part:
                    return part
            
            # No default and not found - fail
            print("FAIL: template variable '{expr}' not found", file=sys.stderr)
            sys.exit(1)
        
        return re.sub(pattern, replacer, text)