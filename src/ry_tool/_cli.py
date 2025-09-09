"""
Lightweight CLI framework for ry.
A mini framework tailored for ry's command parsing needs.
"""

import sys
from typing import Dict, List, Callable, Optional
from dataclasses import dataclass


@dataclass
class Command:
    """Represents a CLI command."""

    name: str
    handler: Callable
    help: str
    requires_arg: bool = False
    arg_name: str = "arg"
    arg_help: str = ""


class CLI:
    """Lightweight CLI framework for ry."""

    def __init__(self, name: str = "ry", description: str = ""):
        self.name = name
        self.description = description
        self.commands: Dict[str, Command] = {}
        self.default_handler: Optional[Callable] = None

    def command(
        self,
        name: str,
        help: str = "",
        requires_arg: bool = False,
        arg_name: str = "arg",
        arg_help: str = "",
    ):
        """Decorator to register a command."""

        def decorator(func: Callable):
            self.commands[name] = Command(
                name=name,
                handler=func,
                help=help,
                requires_arg=requires_arg,
                arg_name=arg_name,
                arg_help=arg_help,
            )
            return func

        return decorator

    def default(self, func: Callable):
        """Decorator to register the default handler for non-command arguments."""
        self.default_handler = func
        return func

    def run(self, argv: Optional[List[str]] = None):
        """Parse arguments and run the appropriate command."""
        if argv is None:
            argv = sys.argv

        # No arguments - show help
        if len(argv) < 2:
            self.show_help()
            sys.exit(0)

        first_arg = argv[1]
        remaining_args = argv[2:] if len(argv) > 2 else []

        # Check for help
        if first_arg in ["-h", "--help"]:
            self.show_help()
            sys.exit(0)

        # Check if it's a registered command
        if first_arg in self.commands:
            cmd = self.commands[first_arg]

            # Check if command requires an argument
            if cmd.requires_arg and not remaining_args:
                print(f"Error: {first_arg} requires an argument", file=sys.stderr)
                print(
                    f"Usage: {self.name} {first_arg} <{cmd.arg_name}>", file=sys.stderr
                )
                sys.exit(1)

            # Call the handler
            try:
                if cmd.requires_arg:
                    result = cmd.handler(remaining_args[0], *remaining_args[1:])
                else:
                    result = cmd.handler(*remaining_args)

                # Handle result
                if isinstance(result, bool):
                    sys.exit(0 if result else 1)
                elif isinstance(result, int):
                    sys.exit(result)
                else:
                    sys.exit(0)
            except KeyboardInterrupt:
                sys.exit(130)
            except Exception as e:
                print(f"Error: {e}", file=sys.stderr)
                sys.exit(1)

        # Not a command - try default handler
        elif self.default_handler:
            try:
                result = self.default_handler(first_arg, *remaining_args)
                if isinstance(result, bool):
                    sys.exit(0 if result else 1)
                elif isinstance(result, int):
                    sys.exit(result)
                else:
                    sys.exit(0)
            except KeyboardInterrupt:
                sys.exit(130)
            except Exception as e:
                print(f"Error: {e}", file=sys.stderr)
                sys.exit(1)

        else:
            print(f"Unknown command: {first_arg}", file=sys.stderr)
            print(f"Try: {self.name} --help", file=sys.stderr)
            sys.exit(1)

    def show_help(self):
        """Display auto-generated help message."""
        lines = []

        # Header
        lines.append(f"{self.name} - {self.description}")
        lines.append("")

        # Usage
        lines.append("Usage:")
        if self.default_handler:
            lines.append(
                f"  {self.name} <library> [args...] | sh     Execute an installed library"
            )
            lines.append(
                f"  {self.name} <file.yaml> [args...] | sh   Execute a YAML file"
            )
            lines.append(
                f"  {self.name} <library> [args...]          Generate commands (dry run)"
            )
            lines.append("")

        # Group commands by type
        user_commands = {}
        dev_commands = {}

        for name, cmd in sorted(self.commands.items()):
            if name.startswith("--dev-"):
                dev_commands[name] = cmd
            else:
                user_commands[name] = cmd

        # User commands
        if user_commands:
            lines.append("Package Management:")
            for name, cmd in user_commands.items():
                # Format command line
                if cmd.requires_arg:
                    usage = f"{self.name} {name} <{cmd.arg_name}>"
                else:
                    usage = f"{self.name} {name}"
                # Align help text
                lines.append(f"  {usage:<40} {cmd.help}")
            lines.append("")

        # Developer commands
        if dev_commands:
            lines.append("Developer Commands:")
            for name, cmd in dev_commands.items():
                if cmd.requires_arg:
                    usage = f"{self.name} {name} <{cmd.arg_name}>"
                else:
                    usage = f"{self.name} {name}"
                lines.append(f"  {usage:<40} {cmd.help}")
            lines.append("")

        # Examples
        lines.append("Examples:")
        lines.append(f"  {self.name} --install git                Install git library")
        lines.append(
            f'  {self.name} git commit "message" | sh    Execute git commit workflow'
        )
        lines.append(f"  {self.name} workflow.yaml deploy | sh    Execute YAML workflow")
        lines.append(f"  {self.name} uv version                   Generate commands (dry run)")

        print("\n".join(lines))
