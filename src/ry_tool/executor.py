"""
Command executor with multiple language support.

Purpose: Execute commands via subprocess without shell escaping issues.
Supports shell, python, subprocess, and other language execution.
No YAML knowledge, just pure execution.
"""
import subprocess
import sys
import os
import json
import yaml
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from io import StringIO
from pathlib import Path
import ry_tool.utils  # Import ry_tool modules


@dataclass
class ExecutionResult:
    """Result of executing a command."""
    success: bool
    stdout: str = ""
    stderr: str = ""
    returncode: int = 0
    captured_var: Optional[str] = None
    modifications: Optional[Dict[str, Any]] = None


class Executor:
    """
    Execute commands in various modes without shell escaping issues.
    
    Key innovation: Pass strings directly to subprocess, no encoding needed.
    """
    
    def __init__(self, context: Any = None):
        """
        Initialize executor with execution context.
        
        Args:
            context: ExecutionContext object or dict with variables
        """
        # Accept both ExecutionContext objects and dicts
        if hasattr(context, 'to_dict'):
            # It's an ExecutionContext, convert to dict for internal use
            self.context = context.to_dict()
        else:
            self.context = context or {}
        self.dry_run = False
        self.debug = False
    
    def execute_step(self, step: Dict[str, Any], extra_env: Dict[str, str] = None) -> ExecutionResult:
        """
        Execute a single step based on its type.
        
        Args:
            step: Step definition with type and code/command
            extra_env: Additional environment variables
        
        Returns:
            ExecutionResult
        """
        # Merge environment - extra_env takes precedence
        env = {}
        if extra_env:
            env.update(extra_env)
        if step.get('env'):
            env.update(step['env'])
        
        if 'shell' in step:
            return self.execute_shell(step['shell'], env, 
                                    interactive=step.get('interactive', False),
                                    capture_file=step.get('_capture_file'))
        elif 'python' in step:
            return self.execute_python(step['python'], extra_env=env)
        elif 'subprocess' in step:
            return self.execute_subprocess(step['subprocess'])
        elif 'ruby' in step:
            return self.execute_ruby(step['ruby'])
        else:
            raise ValueError(f"Unknown step type: {step.keys()}")
    
    def execute_shell(self, command: str, env: Dict[str, str] = None, 
                     interactive: bool = False, capture_file: str = None) -> ExecutionResult:
        """
        Execute shell command.
        
        Args:
            command: Shell command to execute
            env: Additional environment variables
            interactive: If True, preserve TTY for interactive tools
            capture_file: If provided with interactive, redirect output here
        """
        if self.dry_run:
            return ExecutionResult(
                success=True,
                stdout=f"[DRY RUN] Would execute: {command}"
            )
        
        # Merge environment
        exec_env = os.environ.copy()
        if env:
            exec_env.update(env)
        
        # Add context vars to environment
        for key, value in self.context.items():
            if isinstance(value, (str, int, float, bool)):
                exec_env[f'RY_{key.upper()}'] = str(value)
        
        try:
            if interactive:
                # Interactive mode - preserve TTY
                if capture_file:
                    # Pass capture file as environment variable
                    exec_env['RY_CAPTURE_FILE'] = capture_file
                
                # Run WITHOUT capture_output to preserve TTY
                result = subprocess.run(
                    command,
                    shell=True,
                    env=exec_env
                )
                
                return ExecutionResult(
                    success=result.returncode == 0,
                    stdout="",  # Empty - output went to TTY or file
                    stderr="",
                    returncode=result.returncode
                )
            else:
                # Normal mode with capture
                result = subprocess.run(
                    command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    env=exec_env
                )
                
                return ExecutionResult(
                    success=result.returncode == 0,
                    stdout=result.stdout,
                    stderr=result.stderr,
                    returncode=result.returncode
                )
        except Exception as e:
            return ExecutionResult(
                success=False,
                stderr=str(e),
                returncode=1
            )
    
    def execute_relay(self, target: str, args: List[str], env: Dict[str, str] = None) -> ExecutionResult:
        """
        Relay execution to native command.
        
        Args:
            target: Target binary path (e.g., /usr/bin/git)
            args: Command arguments to pass
            env: Additional environment variables
        
        Returns:
            ExecutionResult
        """
        if self.dry_run:
            return ExecutionResult(
                success=True,
                stdout=f"[DRY RUN] Would relay to: {target} {' '.join(args)}"
            )
        
        # Merge environment
        exec_env = os.environ.copy()
        if env:
            exec_env.update(env)
        
        # Add context vars to environment
        for key, value in self.context.items():
            if isinstance(value, (str, int, float, bool)):
                exec_env[f'RY_{key.upper()}'] = str(value)
        
        try:
            # Direct execution without shell, preserves TTY
            result = subprocess.run(
                [target] + args,
                env=exec_env,
                capture_output=False,  # Direct TTY passthrough
                text=True
            )
            
            return ExecutionResult(
                success=result.returncode == 0,
                stdout="",  # Output went directly to TTY
                stderr="",
                returncode=result.returncode
            )
        except FileNotFoundError:
            return ExecutionResult(
                success=False,
                stderr=f"Command not found: {target}",
                returncode=127
            )
        except Exception as e:
            return ExecutionResult(
                success=False,
                stderr=str(e),
                returncode=1
            )
    
    def execute_python(self, code: str, extra_env: Dict[str, str] = None) -> ExecutionResult:
        """
        Execute Python code with context.
        
        Code has access to context variables and can modify them.
        Modifications are tracked and returned in the ExecutionResult.
        """
        if self.dry_run:
            return ExecutionResult(
                success=True,
                stdout="[DRY RUN] Would execute Python code"
            )
        
        # Helper to safely copy dict/list values
        def safe_copy(value, default):
            if isinstance(value, dict):
                return value.copy()
            elif isinstance(value, list):
                return value.copy()
            return default
        
        # Store original values to detect modifications
        original_flags = safe_copy(self.context.get('flags'), {})
        original_arguments = safe_copy(self.context.get('arguments'), {})
        original_env = safe_copy(self.context.get('env'), {})
        original_captured = safe_copy(self.context.get('captured'), {})
        
        # Set up Python path from environment
        # This allows library code to import from lib/ directories
        if extra_env and 'PYTHONPATH' in extra_env:
            for path in extra_env['PYTHONPATH'].split(':'):
                if path and path not in sys.path:
                    sys.path.insert(0, path)
        
        # Also add library directory if provided
        if extra_env and 'RY_LIBRARY_DIR' in extra_env:
            lib_path = os.path.join(extra_env['RY_LIBRARY_DIR'], 'lib')
            if os.path.exists(lib_path) and lib_path not in sys.path:
                sys.path.insert(0, lib_path)
            
            # Add all sibling library lib/ directories for cross-library imports
            # This allows e.g., uv library to import from git library
            libraries_root = os.path.dirname(extra_env['RY_LIBRARY_DIR'])
            if os.path.exists(libraries_root):
                for item in os.listdir(libraries_root):
                    sibling_lib = os.path.join(libraries_root, item, 'lib')
                    if os.path.isdir(sibling_lib) and sibling_lib not in sys.path:
                        sys.path.insert(0, sibling_lib)
        
        # Merge environment variables into env dict
        merged_env = safe_copy(self.context.get('env'), {})
        if extra_env:
            merged_env.update(extra_env)
        
        # Prepare execution environment with mutable references
        exec_globals = {
            'sys': sys,
            'os': os,
            'subprocess': subprocess,
            'json': json,
            'yaml': yaml,
            'Path': Path,
            'ry_tool': ry_tool,  # Make ry_tool module available
            'flags': safe_copy(self.context.get('flags'), {}),
            'arguments': safe_copy(self.context.get('arguments'), {}),
            'env': merged_env,
            'captured': safe_copy(self.context.get('captured'), {}),
            'remaining_args': self.context.get('remaining_args', []),
            'positionals': safe_copy(self.context.get('positionals'), []),
            'remaining': safe_copy(self.context.get('remaining'), []),
            'context': self.context
        }
        
        # Capture stdout/stderr
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        stdout_capture = StringIO()
        stderr_capture = StringIO()
        
        try:
            sys.stdout = stdout_capture
            sys.stderr = stderr_capture
            
            exec(code, exec_globals)
            
            # Track all modifications
            modifications = {}
            
            # Check for flag modifications
            if 'flags' in exec_globals and exec_globals['flags'] != original_flags:
                modifications['flags'] = exec_globals['flags']
            
            # Check for argument modifications
            if 'arguments' in exec_globals and exec_globals['arguments'] != original_arguments:
                modifications['arguments'] = exec_globals['arguments']
            
            # Check for environment modifications
            if 'env' in exec_globals and exec_globals['env'] != original_env:
                modifications['env'] = exec_globals['env']
            
            # Check for captured variable modifications
            if 'captured' in exec_globals and exec_globals['captured'] != original_captured:
                modifications['captured'] = exec_globals['captured']
            
            # Check for positionals modifications
            if 'positionals' in exec_globals and exec_globals['positionals'] != self.context.get('positionals', []):
                modifications['positionals'] = exec_globals['positionals']
            
            # Check for remaining modifications
            if 'remaining' in exec_globals and exec_globals['remaining'] != self.context.get('remaining', []):
                modifications['remaining'] = exec_globals['remaining']
            
            return ExecutionResult(
                success=True,
                stdout=stdout_capture.getvalue(),
                stderr=stderr_capture.getvalue(),
                returncode=0,
                modifications=modifications if modifications else None
            )
        except SystemExit as e:
            # Even on exit, track modifications
            modifications = {}
            if 'flags' in exec_globals and exec_globals['flags'] != original_flags:
                modifications['flags'] = exec_globals['flags']
            if 'arguments' in exec_globals and exec_globals['arguments'] != original_arguments:
                modifications['arguments'] = exec_globals['arguments']
            if 'env' in exec_globals and exec_globals['env'] != original_env:
                modifications['env'] = exec_globals['env']
            if 'captured' in exec_globals and exec_globals['captured'] != original_captured:
                modifications['captured'] = exec_globals['captured']
            
            return ExecutionResult(
                success=e.code == 0,
                stdout=stdout_capture.getvalue(),
                stderr=stderr_capture.getvalue(),
                returncode=e.code or 0,
                modifications=modifications if modifications else None
            )
        except Exception as e:
            return ExecutionResult(
                success=False,
                stdout=stdout_capture.getvalue(),
                stderr=stderr_capture.getvalue() + str(e),
                returncode=1,
                modifications=None
            )
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr
    
    def execute_subprocess(self, config: Dict[str, Any]) -> ExecutionResult:
        """
        Execute with fine-grained subprocess control.
        
        Args:
            config: {
                'cmd': ['git', 'commit', '-m', 'message'],
                'env': {'KEY': 'value'},
                'cwd': '/path/to/dir',
                'stdin': 'input data',
                'capture': 'stdout'  # or 'stderr' or 'both'
            }
        """
        if self.dry_run:
            return ExecutionResult(
                success=True,
                stdout=f"[DRY RUN] Would execute: {config.get('cmd', [])}"
            )
        
        cmd = config.get('cmd', [])
        if not cmd:
            return ExecutionResult(success=False, stderr="No command specified")
        
        # Prepare subprocess arguments
        kwargs = {
            'capture_output': config.get('capture', True),
            'text': True
        }
        
        if 'env' in config:
            exec_env = os.environ.copy()
            exec_env.update(config['env'])
            kwargs['env'] = exec_env
        
        if 'cwd' in config:
            kwargs['cwd'] = config['cwd']
        
        if 'stdin' in config:
            kwargs['input'] = config['stdin']
        
        try:
            result = subprocess.run(cmd, **kwargs)
            
            return ExecutionResult(
                success=result.returncode == 0,
                stdout=result.stdout if result.stdout else "",
                stderr=result.stderr if result.stderr else "",
                returncode=result.returncode
            )
        except Exception as e:
            return ExecutionResult(
                success=False,
                stderr=str(e),
                returncode=1
            )
    
    def execute_ruby(self, code: str) -> ExecutionResult:
        """Execute Ruby code."""
        if self.dry_run:
            return ExecutionResult(
                success=True,
                stdout="[DRY RUN] Would execute Ruby code"
            )
        
        # Write context as JSON for Ruby to read
        context_json = json.dumps(self.context)
        
        # Ruby wrapper to load context
        ruby_code = f"""
require 'json'
context = JSON.parse('{context_json}')
flags = context['flags'] || {{}}
env = context['env'] || {{}}

{code}
"""
        
        try:
            result = subprocess.run(
                ['ruby', '-e', ruby_code],
                capture_output=True,
                text=True
            )
            
            return ExecutionResult(
                success=result.returncode == 0,
                stdout=result.stdout,
                stderr=result.stderr,
                returncode=result.returncode
            )
        except FileNotFoundError:
            return ExecutionResult(
                success=False,
                stderr="Ruby not found",
                returncode=127
            )
        except Exception as e:
            return ExecutionResult(
                success=False,
                stderr=str(e),
                returncode=1
            )
    
    def show_execution_plan(self, steps: List[Dict[str, Any]]) -> str:
        """
        Show what would be executed (for --ry-run mode).
        
        Returns formatted execution plan.
        """
        plan = ["=== Execution Plan ==="]
        
        for i, step in enumerate(steps, 1):
            if 'shell' in step:
                cmd = step['shell'].strip().replace('\n', ' ')[:80]
                plan.append(f"{i}. Shell: {cmd}{'...' if len(step['shell']) > 80 else ''}")
            
            elif 'python' in step:
                lines = step['python'].strip().split('\n')
                first_line = lines[0][:60] if lines else "<empty>"
                plan.append(f"{i}. Python: {first_line}{'...' if len(lines) > 1 else ''}")
            
            elif 'subprocess' in step:
                cmd = step['subprocess'].get('cmd', [])
                plan.append(f"{i}. Subprocess: {' '.join(cmd)}")
            
            elif 'ruby' in step:
                lines = step['ruby'].strip().split('\n')
                first_line = lines[0][:60] if lines else "<empty>"
                plan.append(f"{i}. Ruby: {first_line}{'...' if len(lines) > 1 else ''}")
            
            elif 'relay' in step and step['relay'] == 'native':
                target = self.context.get('target', 'native-command')
                plan.append(f"{i}. Relay: {target}")
            
            elif 'require' in step:
                plan.append(f"{i}. Require: {step['require']}")
                if 'error' in step:
                    plan.append(f"   Error if missing: {step['error'][:60]}...")
            
            elif 'capture' in step:
                plan.append(f"{i}. Capture: {step['capture']}")
                if 'shell' in step:
                    cmd = step['shell'].strip()[:60]
                    plan.append(f"   Via shell: {cmd}...")
            
            elif 'error' in step:
                plan.append(f"{i}. Error: {step['error']}")
        
        return "\n".join(plan)

