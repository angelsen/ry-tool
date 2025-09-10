"""
Execution context that holds all variables available to templates and execution.

Purpose: Single source of truth for all execution variables.
Provides flags, arguments, environment, and computed values.
No execution logic, just data management.
"""
import os
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from pathlib import Path


@dataclass
class ExecutionContext:
    """
    Complete context for command execution.
    
    This is what templates and code blocks have access to.
    """
    # From parsed command
    command: str = ""
    subcommand: Optional[str] = None
    flags: Dict[str, Any] = field(default_factory=dict)
    arguments: Dict[str, Any] = field(default_factory=dict)  # Named arguments
    positionals: List[str] = field(default_factory=list)      # Unnamed positionals
    remaining: List[str] = field(default_factory=list)        # After --
    remaining_args: List[str] = field(default_factory=list)   # All args for relay
    
    # From environment
    env: Dict[str, str] = field(default_factory=dict)
    cwd: Path = field(default_factory=Path.cwd)
    
    # From library
    library_name: str = ""
    library_version: str = ""
    library_path: Optional[Path] = None
    target: Optional[str] = None  # Native command path
    
    # Runtime values
    captured: Dict[str, str] = field(default_factory=dict)  # Captured variables
    
    def __post_init__(self):
        """Initialize with current environment."""
        if not self.env:
            self.env = dict(os.environ)
    
    def get(self, path: str, default: Any = None) -> Any:
        """
        Get value by dot-notation path.
        
        Examples:
            ctx.get('flags.message')
            ctx.get('env.USER')
            ctx.get('arguments.branch', 'main')
        """
        parts = path.split('.')
        value = self
        
        for part in parts:
            if hasattr(value, part):
                value = getattr(value, part)
            elif isinstance(value, dict):
                value = value.get(part)
                if value is None:
                    return default
            elif isinstance(value, list):
                try:
                    index = int(part)
                    value = value[index] if index < len(value) else default
                except (ValueError, IndexError):
                    return default
            else:
                return default
        
        return value
    
    def set(self, path: str, value: Any):
        """
        Set value by dot-notation path.
        
        Examples:
            ctx.set('flags.token', 'abc123')
            ctx.set('captured.BUILD_TOKEN', 'xyz')
        """
        parts = path.split('.')
        target = self
        
        # Navigate to parent
        for part in parts[:-1]:
            if hasattr(target, part):
                target = getattr(target, part)
            elif isinstance(target, dict):
                if part not in target:
                    target[part] = {}
                target = target[part]
        
        # Set the value
        last_part = parts[-1]
        if hasattr(target, last_part):
            setattr(target, last_part, value)
        elif isinstance(target, dict):
            target[last_part] = value
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert context to dictionary for template rendering.
        
        Returns flat and nested versions for convenience.
        """
        return {
            # Direct access
            'command': self.command,
            'subcommand': self.subcommand,
            'flags': self.flags,
            'arguments': self.arguments,
            'positionals': self.positionals,
            'remaining': self.remaining,
            'remaining_args': self.remaining_args,  # Full args for relay
            'env': self.env,
            'cwd': str(self.cwd),
            'library_name': self.library_name,
            'library_version': self.library_version,
            'captured': self.captured,
            
            # Computed values
            'original': self._reconstruct_original(),
            'relay': self._build_relay_command(),
            'relay_base': self.target or self.command,
        }
    
    def _reconstruct_original(self) -> str:
        """Reconstruct original command line."""
        parts = [self.command]
        
        if self.subcommand:
            parts.append(self.subcommand)
        
        # Add flags
        for key, value in self.flags.items():
            if len(key) == 1:
                parts.append(f'-{key}')
            else:
                parts.append(f'--{key}')
            
            if value is not True:  # Not a boolean flag
                parts.append(str(value))
        
        # Add positionals
        parts.extend(self.positionals)
        
        # Add remaining after --
        if self.remaining:
            parts.append('--')
            parts.extend(self.remaining)
        
        return ' '.join(parts)
    
    def _build_relay_command(self) -> str:
        """Build command for relaying to native tool."""
        if not self.target:
            return self._reconstruct_original()
        
        parts = [self.target, self.command]
        
        if self.subcommand:
            parts.append(self.subcommand)
        
        # Add all flags and args as-is
        for key, value in self.flags.items():
            if len(key) == 1:
                parts.append(f'-{key}')
            else:
                parts.append(f'--{key}')
            
            if value is not True:
                parts.append(str(value))
        
        parts.extend(self.positionals)
        
        if self.remaining:
            parts.append('--')
            parts.extend(self.remaining)
        
        return ' '.join(parts)
    
    def rebuild_remaining_args(self) -> List[str]:
        """
        Rebuild remaining_args from current flag/argument values.
        This is needed after before hooks modify flags.
        """
        args = []
        
        # Add command
        if self.command:
            args.append(self.command)
        
        # Add subcommand if present
        if self.subcommand:
            args.append(self.subcommand)
        
        # Add positionals before flags (typical order)
        args.extend(self.positionals)
        
        # Add flags with current values
        for key, value in self.flags.items():
            if len(key) == 1:
                args.append(f'-{key}')
            else:
                args.append(f'--{key}')
            
            if value is not True:
                args.append(str(value))
        
        # Add remaining after --
        if self.remaining:
            args.append('--')
            args.extend(self.remaining)
        
        return args
    
    def apply_modifications(self, mods: Dict[str, Any]):
        """
        Apply modifications from execution steps.
        
        This is the central method for updating context state after
        execution steps that modify flags, arguments, or environment.
        
        Args:
            mods: Dictionary of modifications to apply
                  Keys can be: flags, arguments, env, captured, positionals
        """
        if not mods:
            return
            
        # Apply flag modifications
        if 'flags' in mods:
            # Update flags with new values
            if isinstance(mods['flags'], dict):
                self.flags.update(mods['flags'])
            else:
                self.flags = mods['flags']
            # Rebuild remaining_args to reflect flag changes
            self.remaining_args = self.rebuild_remaining_args()
        
        # Apply argument modifications
        if 'arguments' in mods:
            if isinstance(mods['arguments'], dict):
                self.arguments.update(mods['arguments'])
            else:
                self.arguments = mods['arguments']
        
        # Apply environment modifications
        if 'env' in mods:
            if isinstance(mods['env'], dict):
                self.env.update(mods['env'])
            else:
                self.env = mods['env']
        
        # Apply captured variable modifications
        if 'captured' in mods:
            if isinstance(mods['captured'], dict):
                self.captured.update(mods['captured'])
            else:
                self.captured = mods['captured']
        
        # Apply positional modifications
        if 'positionals' in mods:
            self.positionals = mods['positionals']
            # Rebuild remaining_args if positionals changed
            self.remaining_args = self.rebuild_remaining_args()
        
        # Apply remaining modifications
        if 'remaining' in mods:
            self.remaining = mods['remaining']
            # Rebuild remaining_args if remaining changed
            self.remaining_args = self.rebuild_remaining_args()
    
    def copy(self) -> 'ExecutionContext':
        """Create a deep copy of the context."""
        return ExecutionContext(
            command=self.command,
            subcommand=self.subcommand,
            flags=self.flags.copy(),
            arguments=self.arguments.copy(),
            positionals=self.positionals.copy(),
            remaining=self.remaining.copy(),
            remaining_args=self.remaining_args.copy(),
            env=self.env.copy(),
            cwd=self.cwd,
            library_name=self.library_name,
            library_version=self.library_version,
            library_path=self.library_path,
            target=self.target,
            captured=self.captured.copy()
        )

