"""
Step normalizer - converts various YAML structures to canonical form.
Single responsibility: transform user-friendly YAML to executor-ready format.
"""
from typing import Any, Dict


class Normalizer:
    """Normalize YAML structures to canonical step format."""
    
    def normalize_step(self, step: Any) -> Dict[str, Any]:
        """
        Convert any step format to canonical form.
        
        Canonical form:
        {
            'executor': 'shell|python|etc',
            'script': 'actual code',
            'config': {...},  # Optional executor config
            'capture': 'VAR_NAME',  # Optional variable capture
            'test': 'condition'  # Optional test condition
        }
        """
        if isinstance(step, str):
            # Plain string = shell command
            return {'executor': 'shell', 'script': step}
        
        if not isinstance(step, dict):
            return {'executor': 'shell', 'script': 'echo "ERROR: Invalid step type" >&2; exit 1'}
        
        # Extract special directives first (not part of config)
        capture_var = step.pop('capture', None) if 'capture' in step else None
        test_condition = step.pop('test', None) if 'test' in step else None
        fail_message = step.pop('fail', None) if 'fail' in step else None
        
        # Check for executor keys (python, shell, etc.)
        normalized = None
        for key in ['python', 'py', 'shell', 'sh', 'bash']:
            if key in step:
                value = step[key]
                
                # Handle complex form: python: {script: "...", config...}
                if isinstance(value, dict):
                    script = value.pop('script', '')
                    normalized = {
                        'executor': self._normalize_executor_name(key),
                        'script': script,
                        'config': value  # Rest is config
                    }
                else:
                    # Simple form: python: "..."
                    # Don't include special directives in config
                    config = {k: v for k, v in step.items() 
                             if k not in [key, 'capture', 'test', 'fail']}
                    normalized = {
                        'executor': self._normalize_executor_name(key),
                        'script': value,
                        'config': config if config else None
                    }
                break
        
        if not normalized:
            # No recognized executor, treat as error
            return {'executor': 'shell', 'script': f'echo "ERROR: Unknown step type" >&2; exit 1'}
        
        # Add special directives back to normalized form
        if capture_var:
            normalized['capture'] = capture_var
        if test_condition:
            normalized['test'] = test_condition
        if fail_message:
            normalized['fail'] = fail_message
            
        return normalized
        
        # Handle special constructs
        if 'fail' in step:
            return self._normalize_fail(step)
        
        if 'warn' in step:
            return self._normalize_warn(step)
        
        if 'test' in step:
            return self._normalize_test(step)
        
        if 'export' in step:
            return self._normalize_export(step)
        
        # Default: treat as shell
        return {'executor': 'shell', 'script': '# Unknown step type'}
    
    def _normalize_executor_name(self, name: str) -> str:
        """Map aliases to canonical executor names."""
        mapping = {
            'py': 'python',
            'sh': 'shell',
            'bash': 'shell',
            'zsh': 'shell'
        }
        return mapping.get(name, name)
    
    def _normalize_fail(self, step: Dict) -> Dict[str, Any]:
        """Convert fail step to shell script."""
        msg = step['fail']
        code = step.get('code', 1)
        hints = step.get('hints', [])
        
        lines = [f'echo "FAIL: {msg}" >&2']
        for hint in hints:
            lines.append(f'echo "  Run: {hint}" >&2')
        lines.append(f'exit {code}')
        
        return {
            'executor': 'shell',
            'script': '\n'.join(lines)
        }
    
    def _normalize_warn(self, step: Dict) -> Dict[str, Any]:
        """Convert warn step to shell script."""
        return {
            'executor': 'shell',
            'script': f'echo "WARN: {step["warn"]}" >&2'
        }
    
    def _normalize_test(self, step: Dict) -> Dict[str, Any]:
        """Convert test step to shell script."""
        test_cmd = step['test']
        
        if 'fail' in step:
            fail_cmd = step['fail']
            script = f"{test_cmd} || ({fail_cmd})"
        else:
            script = test_cmd
        
        return {
            'executor': 'shell',
            'script': script
        }
    
    def _normalize_export(self, step: Dict) -> Dict[str, Any]:
        """Convert export step to shell script."""
        exports = []
        for key, value in step['export'].items():
            exports.append(f'export {key}="{value}"')
        
        return {
            'executor': 'shell',
            'script': '\n'.join(exports)
        }