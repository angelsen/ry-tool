"""
Template processor for variable substitution.

Purpose: Replace template variables like {{flags.m}} with actual values.
Simple and focused - just template substitution, no execution logic.
"""
import re
from typing import Any, Dict, TypeVar, Callable
from .context import ExecutionContext

# Generic type for recursive processing
T = TypeVar('T')


class TemplateProcessor:
    """
    Process templates with variable substitution.
    
    Supports:
    - Simple variables: {{flags.m}}
    - Defaults: {{flags.m|default:"no message"}}
    - Filters: {{flags.m|upper}}, {{positionals|join:", "}}
    """
    
    def __init__(self, context: ExecutionContext):
        """
        Initialize with execution context.
        
        Args:
            context: ExecutionContext with all available variables
        """
        self.context = context
        self.filters = self._build_filters()
    
    def process(self, template: str) -> str:
        """
        Process template string, replacing all variables.
        
        Args:
            template: String with {{variable}} placeholders
        
        Returns:
            Processed string with variables replaced
        """
        if not isinstance(template, str):
            return str(template)
        
        # Find all template variables
        pattern = r'\{\{([^}]+)\}\}'
        
        def replace_var(match):
            var_expr = match.group(1).strip()
            return str(self._evaluate_expression(var_expr))
        
        return re.sub(pattern, replace_var, template)
    
    def process_recursive(self, data: T) -> T:
        """
        Recursively process any data structure containing templates.
        
        Uses type dispatch for clean handling of different data types.
        
        Args:
            data: Any data structure potentially containing template strings
        
        Returns:
            Data structure with all templates processed
        """
        return self._dispatch_process(data)
    
    def _dispatch_process(self, data: Any) -> Any:
        """Type-based dispatch for processing different data types."""
        if isinstance(data, str):
            return self.process(data)
        elif isinstance(data, dict):
            return {key: self._dispatch_process(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [self._dispatch_process(item) for item in data] 
        elif isinstance(data, tuple):
            return tuple(self._dispatch_process(item) for item in data)
        else:
            return data
    
    
    def _evaluate_expression(self, expr: str) -> Any:
        """
        Evaluate a template expression.
        
        Handles:
        - Simple paths: flags.m
        - Defaults: flags.m|default:"none"
        - Filters: flags.m|upper
        """
        # Split by pipe for filters/defaults
        parts = expr.split('|')
        base_expr = parts[0].strip()
        
        # Get base value
        value = self._get_value(base_expr)
        
        # Apply filters/defaults
        for part in parts[1:]:
            part = part.strip()
            if part.startswith('default:'):
                default_val = part[8:].strip().strip('"\'')
                if value is None or value == "":
                    value = default_val
            else:
                # Apply filter
                value = self._apply_filter(value, part)
        
        return value
    
    def _get_value(self, path: str) -> Any:
        """
        Get value from context by path.
        
        Special variables:
        - original: Reconstructed original command
        - relay: Command to relay to native tool
        - relay_base: Just the native tool path
        """
        # Check for special computed values
        if path == 'original':
            return self.context._reconstruct_original()
        elif path == 'relay':
            return self.context._build_relay_command()
        elif path == 'relay_base':
            return self.context.target or self.context.command
        
        # Normal path lookup
        value = self.context.get(path)
        
        # Convert None to empty string
        if value is None:
            return ""
        
        # Convert booleans to shell-friendly strings
        if isinstance(value, bool):
            return "true" if value else ""
        
        return value
    
    def _apply_filter(self, value: Any, filter_name: str) -> Any:
        """Apply a filter to a value."""
        if filter_name in self.filters:
            return self.filters[filter_name](value)
        return value
    
    def _build_filters(self) -> Dict[str, Callable[[Any], Any]]:
        """Build available filters with proper typing."""
        return {
            'upper': self._filter_upper,
            'lower': self._filter_lower, 
            'strip': self._filter_strip,
            'join': self._filter_join,
            'json': self._filter_json,
            'shell_escape': self._filter_shell_escape,
            'strip_prefix': self._filter_strip_prefix,
            'length': self._filter_length,
            'default': self._filter_default,
        }
    
    def _filter_upper(self, x: Any) -> str:
        """Convert to uppercase."""
        return str(x).upper()
    
    def _filter_lower(self, x: Any) -> str:
        """Convert to lowercase."""
        return str(x).lower()
    
    def _filter_strip(self, x: Any) -> str:
        """Strip whitespace."""
        return str(x).strip()
    
    def _filter_join(self, x: Any, delimiter: str = ', ') -> str:
        """Join list items or convert to string."""
        if isinstance(x, list):
            return delimiter.join(str(i) for i in x)
        return str(x)
    
    def _filter_json(self, x: Any) -> str:
        """Convert to JSON string."""
        import json
        return json.dumps(x) if x else "{}"
    
    def _filter_shell_escape(self, x: Any) -> str:
        """Escape for shell usage."""
        import shlex
        return shlex.quote(str(x))
    
    def _filter_strip_prefix(self, x: Any, prefix: str = 'v') -> str:
        """Strip prefix from string."""
        s = str(x)
        return s.lstrip(prefix) if isinstance(x, str) else s
    
    def _filter_length(self, x: Any) -> int:
        """Get length of object."""
        return len(x) if hasattr(x, '__len__') else 0
    
    def _filter_default(self, x: Any, default_val: Any = '') -> Any:
        """Return default if value is falsy."""
        return x if x else default_val
    
    def evaluate_condition(self, condition: str) -> bool:
        """
        Evaluate a conditional expression safely.
        
        Examples:
            flags.force
            not flags.dry_run
            flags.bump == "major"
            arguments.branch in ["main", "master"]
        """
        # Process any template variables first
        processed_condition = self.process(condition)
        
        # Use safe evaluation with restricted builtins
        return self._safe_eval(processed_condition)
    
    def _safe_eval(self, expression: str) -> bool:
        """Safely evaluate boolean expressions."""
        # Create safe evaluation context
        eval_context = self.context.to_dict()
        
        # Allowed builtins for safe evaluation
        safe_builtins = {
            '__builtins__': {
                'len': len,
                'str': str,
                'int': int,
                'float': float,
                'bool': bool,
                'list': list,
                'dict': dict,
                'True': True,
                'False': False,
                'None': None,
            }
        }
        
        try:
            result = eval(expression, safe_builtins, eval_context)
            return bool(result)
        except Exception:
            # Fallback to string comparison for simple cases
            return self._fallback_condition_eval(expression, eval_context)
    
    def _fallback_condition_eval(self, expression: str, context: Dict[str, Any]) -> bool:
        """Fallback condition evaluation for simple cases."""
        # Handle simple true/false checks
        if expression.lower() in ['true', '1', 'yes']:
            return True
        if expression.lower() in ['false', '0', 'no', '']:
            return False
        
        # Check if it's a simple variable lookup
        if expression in context:
            return bool(context[expression])
        
        # Default to False for unknown expressions
        return False
    
    def process_modifications(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process modification directives in a step.
        
        Supports explicit modification syntax for cleaner YAML:
            modify:
                flags.message: "cleaned message"
                env.TOKEN: "{{captured.token}}"
        
        Args:
            step: Step dictionary potentially containing 'modify' directive
        
        Returns:
            Dictionary of modifications to apply to context
        """
        if 'modify' not in step:
            return {}
        
        modifications = {}
        modify_spec = step['modify']
        
        for path, value in modify_spec.items():
            # Process template in value
            processed_value = self.process(value) if isinstance(value, str) else value
            
            # Parse the path (e.g., "flags.message" -> modify flags)
            parts = path.split('.')
            if len(parts) == 2:
                category, key = parts
                if category not in modifications:
                    modifications[category] = {}
                if isinstance(modifications[category], dict):
                    modifications[category][key] = processed_value
            elif len(parts) == 1:
                # Direct modification (e.g., "positionals")
                modifications[parts[0]] = processed_value
        
        return modifications


# These are now imported at module level where needed


