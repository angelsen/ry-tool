"""
Shared utilities for reducing boilerplate across ry-next modules.

Contains common patterns for error handling, subprocess execution,
file operations, and other repetitive tasks.
"""
import os
import sys
import json
import subprocess
import functools
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple, Union
from datetime import datetime, date
import yaml


def handle_errors(return_on_error=False, print_prefix="❌"):
    """
    Decorator for consistent error handling across library modules.
    
    Args:
        return_on_error: Value to return on error (False for bool functions)
        print_prefix: Prefix for error messages
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                print(f"{print_prefix} {func.__name__} failed: {e}", file=sys.stderr)
                return return_on_error
        return wrapper
    return decorator


class CommandBuilder:
    """Build subprocess commands with consistent error handling."""
    
    def __init__(self, capture_output=True, text=True, check=False):
        self.capture_output = capture_output
        self.text = text 
        self.check = check
        self.env = None
        self.cwd = None
    
    def with_env(self, env: Dict[str, str]) -> 'CommandBuilder':
        """Add environment variables."""
        self.env = env
        return self
    
    def with_cwd(self, cwd: Union[str, Path]) -> 'CommandBuilder':
        """Set working directory."""
        self.cwd = str(cwd)
        return self
    
    def run(self, cmd: List[str]) -> subprocess.CompletedProcess:
        """Execute command with configured options."""
        kwargs = {
            'capture_output': self.capture_output,
            'text': self.text,
            'check': self.check
        }
        
        if self.env:
            exec_env = os.environ.copy()
            exec_env.update(self.env)
            kwargs['env'] = exec_env
        
        if self.cwd:
            kwargs['cwd'] = self.cwd
            
        return subprocess.run(cmd, **kwargs)
    
    def run_git(self, *args) -> subprocess.CompletedProcess:
        """Execute git command."""
        return self.run(['/usr/bin/git'] + list(args))
    
    def run_uv(self, *args) -> subprocess.CompletedProcess:
        """Execute uv command.""" 
        return self.run(['/usr/bin/uv'] + list(args))


class FileManager:
    """Manage file operations with consistent error handling and validation."""
    
    @staticmethod
    @handle_errors(return_on_error=None)
    def load_yaml(path: Path) -> Optional[Dict[str, Any]]:
        """Load YAML file with error handling."""
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")
        
        with open(path) as f:
            return yaml.safe_load(f)
    
    @staticmethod
    @handle_errors(return_on_error=False)
    def save_yaml(data: Dict[str, Any], path: Path, sort_keys=False) -> bool:
        """Save YAML file with error handling."""
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w') as f:
            yaml.dump(data, f, sort_keys=sort_keys, default_flow_style=False)
        return True
    
    @staticmethod
    @handle_errors(return_on_error=None)
    def load_json(path: Path) -> Optional[Dict[str, Any]]:
        """Load JSON file with error handling."""
        if not path.exists():
            return {}
        
        with open(path) as f:
            return json.load(f)
    
    @staticmethod
    @handle_errors(return_on_error=False)
    def save_json(data: Dict[str, Any], path: Path, indent=2) -> bool:
        """Save JSON file with error handling."""
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w') as f:
            json.dump(data, f, indent=indent, sort_keys=True)
        return True
    
    @staticmethod
    def ensure_dir(path: Path) -> Path:
        """Ensure directory exists and return path."""
        path.mkdir(parents=True, exist_ok=True)
        return path


class VersionManager:
    """Handle semantic version operations."""
    
    @staticmethod
    def parse_version(version: str) -> Tuple[int, int, int]:
        """Parse version string into components."""
        parts = version.split('.')
        major = int(parts[0]) if len(parts) > 0 else 0
        minor = int(parts[1]) if len(parts) > 1 else 0
        patch = int(parts[2]) if len(parts) > 2 else 0
        return major, minor, patch
    
    @staticmethod
    def bump_version(version: str, bump_type: str) -> str:
        """Bump version by type (major, minor, patch)."""
        major, minor, patch = VersionManager.parse_version(version)
        
        if bump_type == 'major':
            major += 1
            minor = patch = 0
        elif bump_type == 'minor':
            minor += 1
            patch = 0
        else:  # patch
            patch += 1
        
        return f"{major}.{minor}.{patch}"
    
    @staticmethod
    def is_valid_version(version: str) -> bool:
        """Check if version string is valid semver."""
        try:
            VersionManager.parse_version(version)
            return True
        except (ValueError, IndexError):
            return False


class LibraryBase:
    """Base class for library operation modules with common functionality."""
    
    def __init__(self, base_path: str = 'docs_next/libraries'):
        self.base_path = Path(base_path)
        self.file_manager = FileManager()
        self.version_manager = VersionManager()
        self.cmd = CommandBuilder()
    
    def get_library_dir(self, name: str) -> Path:
        """Get library directory path."""
        return self.base_path / name
    
    def get_library_yaml(self, name: str) -> Path:
        """Get library YAML file path."""
        return self.get_library_dir(name) / f"{name}.yaml"
    
    def get_meta_yaml(self, name: str) -> Path:
        """Get library meta.yaml path."""
        return self.get_library_dir(name) / "meta.yaml"
    
    def library_exists(self, name: str) -> bool:
        """Check if library exists."""
        return self.get_library_yaml(name).exists()
    
    @handle_errors(return_on_error=None)
    def load_library_config(self, name: str) -> Optional[Dict[str, Any]]:
        """Load library configuration."""
        return self.file_manager.load_yaml(self.get_library_yaml(name))
    
    @handle_errors(return_on_error=None) 
    def load_library_meta(self, name: str) -> Optional[Dict[str, Any]]:
        """Load library metadata."""
        meta_path = self.get_meta_yaml(name)
        if not meta_path.exists():
            return {}
        return self.file_manager.load_yaml(meta_path)
    
    @handle_errors(return_on_error=False)
    def save_library_meta(self, name: str, meta: Dict[str, Any]) -> bool:
        """Save library metadata."""
        meta['updated'] = date.today().isoformat()
        return self.file_manager.save_yaml(meta, self.get_meta_yaml(name))
    
    def get_library_version(self, name: str) -> str:
        """Get current library version."""
        meta = self.load_library_meta(name)
        return meta.get('version', '0.0.0') if meta else '0.0.0'
    
    def list_libraries(self) -> List[str]:
        """List all available libraries."""
        if not self.base_path.exists():
            return []
        
        libraries = []
        for item in self.base_path.iterdir():
            if item.is_dir():
                yaml_file = item / f"{item.name}.yaml"
                if yaml_file.exists():
                    libraries.append(item.name)
        
        return sorted(libraries)
    
    def success_message(self, message: str):
        """Print success message."""
        print(f"✅ {message}")
    
    def info_message(self, message: str):
        """Print info message."""
        print(f"ℹ️  {message}")
    
    def warning_message(self, message: str):
        """Print warning message."""
        print(f"⚠️  {message}")
    
    def error_message(self, message: str):
        """Print error message."""
        print(f"❌ {message}", file=sys.stderr)




def validate_name(name: str) -> bool:
    """Validate library/package name format."""
    return name.replace('-', '').replace('_', '').isalnum()


def get_current_date() -> str:
    """Get current date in ISO format."""
    return date.today().isoformat()


def get_current_datetime() -> str:
    """Get current datetime in ISO format."""
    return datetime.now().isoformat()


class ContextFactory:
    """Factory for building execution contexts with consistent patterns."""
    
    @staticmethod
    def from_parsed_command(parsed, library, command_config=None):
        """
        Build ExecutionContext from parsed command and library.
        
        Centralizes the context building logic that was duplicated
        across matcher.py and app.py.
        """
        from .context import ExecutionContext
        
        # For augmentation libraries, use raw args to preserve exact user input
        # This ensures flags like -10 aren't incorrectly parsed as --10
        if library.type == 'augmentation' and parsed.raw_args:
            # Use ALL raw args - they represent the actual git/tool command
            remaining_args = parsed.raw_args
        else:
            # For other library types, reconstruct from parsed components
            # Build remaining_args for relay (all original args)
            remaining_args = []
            if parsed.command:
                remaining_args.append(parsed.command)
            if parsed.subcommand:
                remaining_args.append(parsed.subcommand)
            remaining_args.extend(parsed.positionals)
            
            # Add flags in original format
            for flag, value in parsed.flags.items():
                if len(flag) == 1:
                    remaining_args.append(f'-{flag}')
                else:
                    remaining_args.append(f'--{flag}')
                if value is not True:
                    remaining_args.append(str(value))
            
            if parsed.remaining:
                remaining_args.append('--')
                remaining_args.extend(parsed.remaining)
        
        context = ExecutionContext(
            command=parsed.command,
            subcommand=parsed.subcommand,
            flags=parsed.flags,
            positionals=parsed.positionals,
            remaining=parsed.remaining,
            remaining_args=remaining_args,
            library_name=library.name,
            library_version=library.metadata.get('version', '0.0.0'),
            library_path=library.path,
            target=library.target
        )
        
        # Map positionals to named arguments if schema provided
        if command_config and 'arguments' in command_config:
            ContextFactory._map_arguments(context, command_config['arguments'])
        
        return context
    
    @staticmethod
    def _map_arguments(context, arg_schema):
        """
        Map positional arguments to named arguments based on schema.
        
        Args:
            context: ExecutionContext to update
            arg_schema: Argument schema from command config
        """
        positionals = context.positionals.copy()
        
        for arg_name, arg_config in arg_schema.items():
            if not positionals:
                # No more positionals to map
                if isinstance(arg_config, dict) and arg_config.get('required'):
                    context.arguments[arg_name] = None
                elif arg_config == 'required':
                    context.arguments[arg_name] = None
                continue
            
            # Map positional to named argument
            if isinstance(arg_config, dict):
                if arg_config.get('multiple'):
                    # Consume all remaining positionals
                    context.arguments[arg_name] = positionals
                    positionals = []
                else:
                    # Consume one positional
                    context.arguments[arg_name] = positionals.pop(0)
            else:
                # Simple required/optional
                context.arguments[arg_name] = positionals.pop(0)
        
        # Update positionals with unmapped ones
        context.positionals = positionals
    
    @staticmethod
    def create_library_env(library):
        """
        Create environment variables for library execution.
        
        Centralizes the env setup logic from app.py.
        """
        import os
        
        env = {
            'RY_LIBRARY_NAME': library.name,
            'RY_LIBRARY_VERSION': library.metadata.get('version', '0.0.0'),
            'RY_LIBRARY_TYPE': library.type,
        }
        
        # Set library directory if it's in standard location
        if library.path:
            if library.path.parent.name == library.name:
                # Directory format - has lib/ folder
                env['RY_LIBRARY_DIR'] = str(library.path.parent)
                
                # Add lib/ to Python path if it exists
                lib_path = library.path.parent / 'lib'
                if lib_path.exists():
                    current_pythonpath = os.environ.get('PYTHONPATH', '')
                    env['PYTHONPATH'] = f"{lib_path}:{current_pythonpath}" if current_pythonpath else str(lib_path)
            else:
                # Single file format
                env['RY_LIBRARY_DIR'] = str(library.path.parent)
            
            env['RY_LIBRARY_PATH'] = str(library.path)
        
        return env