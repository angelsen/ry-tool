"""
Command line parser that understands semantic structure.

Purpose: Convert raw args like ['commit', '-m', 'msg', '--amend'] 
into structured data with flags, arguments, and commands.
No YAML knowledge, just pure argument parsing.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple


@dataclass
class ParsedCommand:
    """Structured representation of a parsed command."""
    command: str
    subcommand: Optional[str] = None
    flags: Dict[str, Any] = field(default_factory=dict)
    positionals: List[str] = field(default_factory=list)
    remaining: List[str] = field(default_factory=list)  # After -- separator
    raw_args: List[str] = field(default_factory=list)   # Original args for reference


class CommandParser:
    """
    Parse command line arguments with flag schema awareness.
    
    This parser understands:
    - Flags with values: -m "message", --package backend
    - Boolean flags: -a, --force
    - Positional arguments
    - Double dash separator: -- 
    - Subcommands: remote add origin
    """
    
    def parse(self, args: List[str], schema: Dict[str, Any] = None) -> ParsedCommand:
        """
        Parse arguments with optional schema for flag types.
        
        Args:
            args: Raw command line arguments
            schema: Optional schema defining flag types
                   {'m': 'string', 'force': 'bool', 'bump': 'enum'}
        
        Returns:
            ParsedCommand with structured data
        """
        if not args:
            return ParsedCommand(command="", raw_args=args)
        
        schema = schema or {}
        result = ParsedCommand(command=args[0], raw_args=args.copy())
        
        i = 1
        while i < len(args):
            arg = args[i]
            
            # Double dash separator
            if arg == '--':
                result.remaining = args[i+1:]
                break
            
            # Flag (short or long)
            if arg.startswith('-'):
                flag_name, flag_value, consumed = self._parse_flag(args, i, schema)
                if flag_name:
                    result.flags[flag_name] = flag_value
                i += consumed
            else:
                # Positional argument
                result.positionals.append(arg)
                i += 1
        
        # Check if first positional might be a subcommand
        if result.positionals and not result.subcommand:
            # This is a simple heuristic - could be enhanced
            if result.command in ['git', 'docker', 'kubectl']:
                result.subcommand = result.positionals.pop(0)
        
        return result
    
    def _parse_flag(self, args: List[str], index: int, schema: Dict) -> Tuple[str, Any, int]:
        """
        Parse a flag and its value if applicable.
        
        Returns:
            (flag_name, flag_value, args_consumed)
        """
        arg = args[index]
        
        # Long flag with = (--message="hello")
        if '--' in arg and '=' in arg:
            flag_part, value = arg.split('=', 1)
            flag_name = flag_part.lstrip('-')
            return flag_name, value, 1
        
        # Regular flag
        flag_name = arg.lstrip('-')
        
        # Check schema for flag type
        flag_type = self._get_flag_type(flag_name, schema)
        
        if flag_type == 'bool':
            return flag_name, True, 1
        
        # Flag takes a value - consume next arg
        if index + 1 < len(args) and not args[index + 1].startswith('-'):
            return flag_name, args[index + 1], 2
        
        # Flag without value (treat as bool)
        return flag_name, True, 1
    
    def _get_flag_type(self, flag_name: str, schema: Dict) -> str:
        """
        Determine flag type from schema.
        
        Handles aliases like m/message.
        """
        if not schema:
            return 'string'  # Default assumption
        
        # Direct match
        if flag_name in schema:
            flag_def = schema[flag_name]
            if isinstance(flag_def, str):
                return flag_def
            elif isinstance(flag_def, dict):
                return flag_def.get('type', 'string')
        
        # Check aliases (m/message format)
        for key, value in schema.items():
            if '/' in key:
                short, long = key.split('/', 1)
                if flag_name in [short, long]:
                    if isinstance(value, str):
                        return value
                    elif isinstance(value, dict):
                        return value.get('type', 'string')
        
        return 'string'  # Default
    
    def parse_with_command_schema(self, args: List[str], command_schema: Dict) -> ParsedCommand:
        """
        Parse with knowledge of command structure.
        
        Args:
            args: Raw arguments
            command_schema: Full command schema with flags and arguments definitions
        
        Returns:
            ParsedCommand with proper typing based on schema
        """
        # Extract flag schema from command schema
        flag_schema = {}
        if 'flags' in command_schema:
            for flag_key, flag_def in command_schema['flags'].items():
                if '/' in flag_key:
                    # Handle m/message style
                    short, long = flag_key.split('/', 1)
                    flag_schema[short] = flag_def
                    flag_schema[long] = flag_def
                else:
                    flag_schema[flag_key] = flag_def
        
        return self.parse(args, flag_schema)
    
    def generate_help(self, library_config, command: str = None) -> str:
        """
        Generate help text for library or specific command.
        
        Args:
            library_config: LibraryConfig object with library metadata
            command: Optional specific command to show help for
        
        Returns:
            Formatted help text
        """
        help_lines = []
        
        if command and command in library_config.commands:
            # Command-specific help
            cmd = library_config.commands[command]
            help_lines.append(f"{library_config.name} {command}")
            
            if 'description' in cmd:
                help_lines.append(f"  {cmd['description']}")
            help_lines.append("")
            
            # Arguments
            if 'arguments' in cmd:
                help_lines.append("Arguments:")
                for arg_name, arg_config in cmd['arguments'].items():
                    if isinstance(arg_config, str):
                        required = arg_config == 'required'
                    else:
                        required = arg_config.get('required', False)
                    desc = arg_config.get('description', '') if isinstance(arg_config, dict) else ''
                    status = 'required' if required else 'optional'
                    help_lines.append(f"  {arg_name:<15} {status:<10} {desc}")
                help_lines.append("")
            
            # Flags
            if 'flags' in cmd:
                help_lines.append("Flags:")
                for flag_name, flag_config in cmd['flags'].items():
                    # Handle alias format (m/message)
                    if '/' in flag_name:
                        short, long = flag_name.split('/', 1)
                        flag_display = f"-{short}, --{long}"
                    else:
                        flag_display = f"--{flag_name}"
                    
                    if isinstance(flag_config, str):
                        flag_type = flag_config
                        desc = ''
                    else:
                        flag_type = flag_config.get('type', 'string')
                        desc = flag_config.get('description', '')
                    
                    help_lines.append(f"  {flag_display:<20} ({flag_type})")
                    if desc:
                        help_lines.append(f"      {desc}")
                help_lines.append("")
            
            # Examples
            if 'examples' in cmd:
                help_lines.append("Examples:")
                for example in cmd['examples']:
                    help_lines.append(f"  {example}")
                help_lines.append("")
        else:
            # Library help - list all commands
            help_lines.append(f"{library_config.name} - {library_config.description}")
            help_lines.append(f"Version: {library_config.version}")
            help_lines.append(f"Type: {library_config.type}")
            help_lines.append("")
            
            if library_config.commands:
                help_lines.append("Commands:")
                for cmd_name, cmd_config in library_config.commands.items():
                    if cmd_name != '*':  # Skip catch-all
                        desc = cmd_config.get('description', 'No description')
                        help_lines.append(f"  {cmd_name:<15} {desc}")
                help_lines.append("")
                help_lines.append("Use: ry-next <library> <command> --help for command details")
        
        return '\n'.join(help_lines)


