"""
Custom YAML loader for ry with powerful tags.
These tags execute at YAML parse time for dynamic configuration.
"""
import os
import yaml
import subprocess
import json
from pathlib import Path
from typing import Any

class RyLoader(yaml.SafeLoader):
    """Custom YAML loader with ry-specific tags."""
    
    def __init__(self, stream):
        super().__init__(stream)
        self.args = []  # Will be set by core

def construct_env(loader: RyLoader, node: yaml.ScalarNode) -> str:
    """Expand environment variables: !env "$USER"."""
    value = loader.construct_scalar(node)
    return os.path.expandvars(value)

def construct_shell(loader: RyLoader, node: yaml.ScalarNode) -> str:
    """Execute shell command and return output: !shell "date +%Y"."""
    cmd = loader.construct_scalar(node)
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=5)
        return result.stdout.strip()
    except Exception:
        return ""

def construct_if(loader: RyLoader, node: yaml.MappingNode) -> Any:
    """Conditional execution: !if {condition: ..., then: ..., else: ...}."""
    data = loader.construct_mapping(node)
    
    condition = data.get('condition', False)
    
    # Evaluate condition
    if isinstance(condition, bool):
        result = condition
    elif isinstance(condition, str):
        # Check if it's a simple comparison
        if '==' in condition:
            left, right = condition.split('==', 1)
            result = left.strip() == right.strip()
        elif '!=' in condition:
            left, right = condition.split('!=', 1)
            result = left.strip() != right.strip()
        elif condition in ['true', 'True', '1']:
            result = True
        elif condition in ['false', 'False', '0', '']:
            result = False
        else:
            # Check as environment variable
            result = bool(os.environ.get(condition))
    else:
        result = bool(condition)
    
    if result:
        return data.get('then', None)
    else:
        return data.get('else', None)

def construct_include(loader: RyLoader, node: yaml.ScalarNode) -> Any:
    """Include another YAML file: !include common.yaml."""
    filename = loader.construct_scalar(node)
    
    # Resolve relative to current file or working directory
    include_path = Path(filename)
    if not include_path.is_absolute():
        # Try relative to current YAML file location
        if hasattr(loader, 'name') and loader.name:
            yaml_dir = Path(loader.name).parent
            include_path = yaml_dir / filename
    
    if include_path.exists():
        with open(include_path) as f:
            return yaml.load(f, Loader=RyLoader)
    
    return {}

def construct_json(loader: RyLoader, node: yaml.ScalarNode) -> Any:
    """Load JSON data: !json file.json or !json '{...}'."""
    value = loader.construct_scalar(node)
    
    # Check if it's a file or inline JSON
    if value.startswith('{') or value.startswith('['):
        # Inline JSON
        return json.loads(value)
    else:
        # File path
        json_path = Path(value)
        if json_path.exists():
            with open(json_path) as f:
                return json.load(f)
    
    return {}

def construct_eval(loader: RyLoader, node: yaml.ScalarNode) -> Any:
    """Evaluate Python expression safely: !eval "len(args) > 0"."""
    expr = loader.construct_scalar(node)
    
    # Safe evaluation context
    safe_context = {
        'args': loader.args,
        'env': os.environ,
        'len': len,
        'str': str,
        'int': int,
        'bool': bool,
        'abs': abs,
        'min': min,
        'max': max,
        'sum': sum,
        'any': any,
        'all': all,
    }
    
    try:
        return eval(expr, {"__builtins__": {}}, safe_context)
    except Exception:
        return False

def construct_exists(loader: RyLoader, node: yaml.ScalarNode) -> bool:
    """Check if file/directory exists: !exists "path"."""
    path = loader.construct_scalar(node)
    return Path(path).exists()

def construct_read(loader: RyLoader, node: yaml.ScalarNode) -> str:
    """Read file contents: !read "file.txt"."""
    path = loader.construct_scalar(node)
    try:
        return Path(path).read_text().strip()
    except Exception:
        return ""

# Register all constructors
RyLoader.add_constructor('!env', construct_env)
RyLoader.add_constructor('!shell', construct_shell)
RyLoader.add_constructor('!if', construct_if)
RyLoader.add_constructor('!include', construct_include)
RyLoader.add_constructor('!json', construct_json)
RyLoader.add_constructor('!eval', construct_eval)
RyLoader.add_constructor('!exists', construct_exists)
RyLoader.add_constructor('!read', construct_read)