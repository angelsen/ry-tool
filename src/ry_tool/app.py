"""
Main application for ry.

Purpose: Wire together all core modules to execute augmented commands.
No package management, just pure command augmentation.
"""
import sys
import os
import tempfile
import hashlib
from pathlib import Path

from ._cli import CLI
from .parser import CommandParser
from .loader import LibraryLoader
from .matcher import CommandMatcher
from .executor import Executor
from .template import TemplateProcessor
from .installer import LibraryInstaller
from .utils import ContextFactory


# Create the CLI app
app = CLI(name="ry", description="Command augmentation framework")




# Note: --ry-run is handled as a global flag in CLI


@app.command("--version", help="Show version")
def show_version():
    """Show ry version."""
    from . import __version__
    print(f"ry {__version__}")
    return True


@app.command("--list", help="List available libraries")
def list_libraries(installed: bool = False, verbose: bool = False):
    """List libraries with source information."""
    loader = LibraryLoader()
    
    if installed:
        # Show only installed libraries
        installer = LibraryInstaller()
        installed_libs = installer.list_installed()
        if installed_libs:
            print("Installed libraries:")
            for name, info in installed_libs.items():
                print(f"  • {name} (v{info.get('version', '0.0.0')})")
        else:
            print("No libraries installed")
        return True
    
    # Show all available libraries
    if verbose:
        print("Available libraries by source:")
        for path in loader.library_paths:
            libs = loader.list_from_path(path)
            if libs:
                # Identify source type
                if "docs_next" in str(path):
                    source = "📁 workspace"
                elif ".local/share" in str(path):
                    source = "👤 user"
                elif ".cache" in str(path):
                    source = "🌐 cached"
                else:
                    source = "📦 system"
                
                print(f"\n{source} ({path}):")
                for lib in libs:
                    print(f"  • {lib}")
    else:
        libraries = loader.list_available()
        if libraries:
            print("Available libraries:")
            for lib in libraries:
                print(f"  • {lib}")
        else:
            print("No libraries found")
            print("Add libraries to:")
            print("  • ./docs/libraries/")
            print("  • ~/.local/share/ry/libraries/")
    
    return True


@app.command("--install", help="Install a library")
def install_library(library_name: str):
    """
    Install library from registry or local source.
    
    Examples:
        ry --install git              # From registry
        ry --install ./my-lib.yaml    # From local file
    """
    installer = LibraryInstaller()
    loader = LibraryLoader()
    
    try:
        if library_name.endswith('.yaml'):
            # Install from local file
            library = loader.load_file(Path(library_name))
            if installer.install_local(library):
                print(f"✅ Installed {library.name} from {library_name}")
            else:
                print(f"❌ Failed to install {library_name}")
                return False
        else:
            # Install from registry/available sources
            if installer.install_from_registry(library_name):
                print(f"✅ Installed {library_name}")
            else:
                return False
    except Exception as e:
        print(f"❌ Installation failed: {e}")
        return False
    
    return True

@app.command("--uninstall", help="Uninstall a library")
def uninstall_library(library_name: str):
    """Uninstall an installed library."""
    installer = LibraryInstaller()
    return installer.uninstall(library_name)

# Default handler for library execution
@app.default
def execute_library(library_name: str, *args):
    """
    Execute a library command.
    
    Args:
        library_name: Name of library or path to YAML file
        args: Command and arguments to execute
    """
    # Check for --ry-run flag from CLI global flags
    ry_run = app.global_flags.get('ry_run', False)
    
    # Check for ry-help flag early (avoid conflict with native --help)
    if '--ry-help' in args:
        # Remove help flag from args
        args = [a for a in args if a != '--ry-help']
        show_help = True
    else:
        show_help = False
    
    # Initialize components
    parser = CommandParser()
    loader = LibraryLoader()
    matcher = CommandMatcher()
    
    # Load library
    try:
        if library_name.endswith('.yaml'):
            # Direct YAML file
            library = loader.load_file(Path(library_name))
        else:
            # Library by name
            library = loader.load(library_name)
    except FileNotFoundError:
        print(f"Library not found: {library_name}", file=sys.stderr)
        print(f"Available libraries: {', '.join(loader.list_available())}", file=sys.stderr)
        return False
    except Exception as e:
        print(f"Failed to load library: {e}", file=sys.stderr)
        return False
    
    # Handle help request
    if show_help:
        help_text = parser.generate_help(library, args[0] if args else None)
        print(help_text)
        return True
    
    # Setup library environment using factory
    library_env = ContextFactory.create_library_env(library)
    
    # Parse command
    parsed = parser.parse_with_command_schema(
        list(args),
        library.commands.get(args[0] if args else '', {})
    )
    
    # Match to handler
    match_result = matcher.match(parsed, library)
    
    if not match_result.matched:
        print(f"No matching command: {match_result.reason}", file=sys.stderr)
        # Show available commands
        if library.commands:
            print(f"Available commands in {library.name}:", file=sys.stderr)
            for cmd in library.commands.keys():
                if cmd != '*':  # Skip catch-all
                    print(f"  • {cmd}", file=sys.stderr)
        return False
    
    # Check if this is an augmentation/relay command
    handler = match_result.handler
    
    # Create executor with library environment
    executor_context = {**match_result.context.to_dict(), 'env': library_env}
    executor = Executor(context=executor_context)
    
    # Handle relay/augmentation mode
    # Check for relay in handler directly OR in augment section (for conditional handlers)
    has_relay = ('relay' in handler and handler['relay'] == 'native') or \
                ('augment' in handler and 'relay' in handler['augment'] and handler['augment']['relay'] == 'native')
    
    if has_relay:
        # This is an augmentation command
        target = library.target or parsed.command
        
        # Execute before hooks if present
        if 'augment' in handler and 'before' in handler['augment']:
            template_processor = TemplateProcessor(match_result.context)
            before_steps = template_processor.process_recursive(handler['augment']['before'])
            
            if ry_run:
                print("# Before hooks:")
                for step in before_steps:
                    print(f"  {step}")
            else:
                for step in before_steps:
                    # Handle special directives
                    if 'require' in step:
                        # Check requirement
                        value = match_result.context.get(step['require'])
                        if not value:
                            error = step.get('error', f"Requirement not met: {step['require']}")
                            print(f"ERROR: {error}", file=sys.stderr)
                            return False
                        continue
                    
                    if 'error' in step:
                        # Show error and exit
                        print(f"ERROR: {step['error']}", file=sys.stderr)
                        return False
                    
                    # Normal execution
                    result = executor.execute_step(step, library_env)
                    
                    # Apply any modifications from the step
                    if result.modifications:
                        match_result.context.apply_modifications(result.modifications)
                    
                    # Show output from before hooks
                    if result.stderr:
                        print(result.stderr, end='', file=sys.stderr)
                    if result.stdout:
                        print(result.stdout, end='')
                    if not result.success:
                        return False
        
        # Relay to native command
        if ry_run:
            print(f"# Relay to: {target} {' '.join(match_result.context.remaining_args)}")
        else:
            result = executor.execute_relay(target, match_result.context.remaining_args, library_env)
            if not result.success:
                return False
        
        # Execute after hooks if present
        if 'augment' in handler and 'after' in handler['augment']:
            template_processor = TemplateProcessor(match_result.context)
            after_steps = template_processor.process_recursive(handler['augment']['after'])
            
            if ry_run:
                print("# After hooks:")
                for step in after_steps:
                    print(f"  {step}")
            else:
                for step in after_steps:
                    # Handle special directives
                    if 'require' in step:
                        value = match_result.context.get(step['require'])
                        if not value:
                            error = step.get('error', f"Requirement not met: {step['require']}")
                            print(f"ERROR: {error}", file=sys.stderr)
                            return False
                        continue
                    
                    if 'error' in step:
                        print(f"ERROR: {step['error']}", file=sys.stderr)
                        return False
                    
                    # Normal execution
                    result = executor.execute_step(step, library_env)
                    
                    # Apply any modifications from the step
                    if result.modifications:
                        match_result.context.apply_modifications(result.modifications)
                    
                    # Show output from after hooks (typically to stderr for info messages)
                    if result.stderr:
                        print(result.stderr, end='', file=sys.stderr)
                    if result.stdout:
                        print(result.stdout, end='')
                    if not result.success:
                        return False
        
        return True
    
    # Normal execution mode (not augmentation)
    # Get execution steps
    steps = matcher.get_execution_plan(match_result)
    
    # Process templates in steps
    template_processor = TemplateProcessor(match_result.context)
    processed_steps = template_processor.process_recursive(steps)
    
    if ry_run:
        # Show execution plan
        plan = executor.show_execution_plan(processed_steps)
        print(plan)
        return True
    
    # Execute steps
    for i, step in enumerate(processed_steps):
        try:
            # Handle special directives
            if 'require' in step:
                # Check requirement
                value = match_result.context.get(step['require'])
                if not value:
                    error = step.get('error', f"Requirement not met: {step['require']}")
                    print(f"ERROR: {error}", file=sys.stderr)
                    return False
                continue
            
            if 'capture' in step:
                # Execute and capture variable
                var_name = step['capture']
                exec_step = {k: v for k, v in step.items() if k != 'capture'}
                
                # Handle interactive capture with tempfile
                if exec_step.get('interactive'):
                    # Create temp file with hash-based name
                    temp_dir = tempfile.gettempdir()
                    hash_name = hashlib.md5(f"ry-{var_name}-{i}".encode()).hexdigest()[:12]
                    capture_file = os.path.join(temp_dir, f"ry-capture-{hash_name}")
                    exec_step['_capture_file'] = capture_file
                    
                    # Execute with TTY preserved
                    result = executor.execute_step(exec_step, library_env)
                    
                    if result.success and os.path.exists(capture_file):
                        # Read captured value from file
                        with open(capture_file, 'r') as f:
                            value = f.read().strip()
                        os.unlink(capture_file)  # Clean up
                        
                        match_result.context.set(f'captured.{var_name}', value)
                        executor.context['captured'][var_name] = value
                    else:
                        print(f"Failed to capture {var_name} (interactive)", file=sys.stderr)
                        if not os.path.exists(capture_file):
                            print(f"Capture file not created: {capture_file}", file=sys.stderr)
                        return False
                else:
                    # Normal capture from stdout
                    result = executor.execute_step(exec_step, library_env)
                    if result.success:
                        value = result.stdout.strip()
                        match_result.context.set(f'captured.{var_name}', value)
                        executor.context['captured'][var_name] = value
                    else:
                        print(f"Failed to capture {var_name}", file=sys.stderr)
                        if result.stderr:
                            print(result.stderr, file=sys.stderr)
                        return False
                
                # Re-process remaining steps with updated context
                if i + 1 < len(processed_steps):
                    template_processor = TemplateProcessor(match_result.context)
                    processed_steps[i+1:] = template_processor.process_recursive(steps[i+1:])
                
                continue
            
            if 'error' in step:
                # Show error and exit
                print(f"ERROR: {step['error']}", file=sys.stderr)
                return False
            
            # Normal execution (may be interactive without capture)
            result = executor.execute_step(step, library_env)
            
            # Apply any modifications from the step
            if result.modifications:
                match_result.context.apply_modifications(result.modifications)
                # Re-create template processor with updated context for remaining steps
                template_processor = TemplateProcessor(match_result.context)
            
            # Handle output (skip for interactive mode as it goes directly to TTY)
            if not step.get('interactive'):
                if result.stdout:
                    print(result.stdout, end='')
                if result.stderr:
                    print(result.stderr, end='', file=sys.stderr)
            
            # Check for failure
            if not result.success:
                return False
                
        except Exception as e:
            print(f"Execution error: {e}", file=sys.stderr)
            return False
    
    return True


def run():
    """Entry point for the CLI."""
    app.run()


if __name__ == "__main__":
    run()