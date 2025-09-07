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
            return {"executor": "shell", "script": step}

        if not isinstance(step, dict):
            return {
                "executor": "shell",
                "script": 'echo "ERROR: Invalid step type" >&2; exit 1',
            }

        # Extract capture directive (not part of config)
        capture_var = step.pop("capture", None) if "capture" in step else None

        # Initialize normalized
        normalized = None
        
        # Check for executor keys (python, shell, etc.)
        if normalized is None:
            for key in ["python", "py", "shell", "sh", "bash"]:
                if key in step:
                    value = step[key]

                    # Handle complex form: python: {script: "...", config...}
                    if isinstance(value, dict):
                        script = value.pop("script", "")
                        normalized = {
                            "executor": self._normalize_executor_name(key),
                            "script": script,
                            "config": value,  # Rest is config
                        }
                    else:
                        # Simple form: python: "..."
                        # Don't include special directives in config
                        config = {
                            k: v
                            for k, v in step.items()
                            if k not in [key, "capture"]
                        }
                        normalized = {
                            "executor": self._normalize_executor_name(key),
                            "script": value,
                            "config": config if config else None,
                        }
                    break

        if not normalized:
            # No recognized executor, treat as error
            return {
                "executor": "shell",
                "script": 'echo "ERROR: Unknown step type" >&2; exit 1',
            }

        # Add capture directive back to normalized form
        if capture_var:
            normalized["capture"] = capture_var

        return normalized

    def _normalize_executor_name(self, name: str) -> str:
        """Map aliases to canonical executor names."""
        mapping = {"py": "python", "sh": "shell", "bash": "shell", "zsh": "shell"}
        return mapping.get(name, name)
