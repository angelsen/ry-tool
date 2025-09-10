"""
Command matcher that determines which handler to execute.

Purpose: Match parsed commands to library command definitions.
Evaluates conditions to select the right handler.
No execution, just matching logic.
"""
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

from .parser import ParsedCommand
from .loader import LibraryConfig
from .context import ExecutionContext
from .template import TemplateProcessor
from .utils import ContextFactory


@dataclass
class MatchResult:
    """Result of matching a command to a handler."""
    matched: bool
    command_config: Optional[Dict[str, Any]] = None
    handler: Optional[Dict[str, Any]] = None
    context: Optional[ExecutionContext] = None
    reason: str = ""


class CommandMatcher:
    """
    Match parsed commands to library handlers.
    
    Responsibilities:
    - Find matching command in library
    - Evaluate handler conditions
    - Build execution context
    - NO execution
    """
    
    def match(self, parsed: ParsedCommand, library: LibraryConfig) -> MatchResult:
        """
        Match a parsed command to a library handler.
        
        Args:
            parsed: Parsed command from CommandParser
            library: Loaded library configuration
        
        Returns:
            MatchResult with matched handler and context
        """
        # Find matching command in library
        command_config = self._find_command(parsed, library)
        if not command_config:
            return MatchResult(
                matched=False,
                reason=f"No command '{parsed.command}' in library '{library.name}'"
            )
        
        # Build execution context using factory
        context = ContextFactory.from_parsed_command(parsed, library, command_config)
        
        # Find matching handler
        handler = self._find_handler(command_config, context)
        if not handler:
            return MatchResult(
                matched=False,
                reason=f"No matching handler for command '{parsed.command}'"
            )
        
        return MatchResult(
            matched=True,
            command_config=command_config,
            handler=handler,
            context=context
        )
    
    def _find_command(self, parsed: ParsedCommand, library: LibraryConfig) -> Optional[Dict[str, Any]]:
        """
        Find matching command definition in library.
        
        Handles:
        - Exact match: commit
        - Subcommand match: remote add
        - Wildcard: * (catch-all)
        """
        commands = library.commands
        
        # Try exact match
        if parsed.command in commands:
            return commands[parsed.command]
        
        # Try with subcommand
        if parsed.subcommand:
            full_command = f"{parsed.command} {parsed.subcommand}"
            if full_command in commands:
                return commands[full_command]
            
            # Try command with wildcard subcommand
            wildcard = f"{parsed.command} *"
            if wildcard in commands:
                return commands[wildcard]
        
        # Try catch-all
        if '*' in commands:
            return commands['*']
        
        # For augmentation libraries, default to relay if no match
        if library.type == 'augmentation' and library.target:
            # Return a default relay handler
            return {
                'relay': 'native',
                'description': 'Pass through to native command'
            }
        
        return None
    
    
    def _find_handler(self, command_config: Dict[str, Any], 
                     context: ExecutionContext) -> Optional[Dict[str, Any]]:
        """
        Find matching handler based on conditions.
        
        Evaluates 'when' conditions to find the right handler.
        """
        # Simple execution modes (no conditions)
        if 'execute' in command_config:
            return {'execute': command_config['execute']}
        
        # Check for augmentation with relay (common pattern)
        if 'augment' in command_config and 'relay' in command_config:
            return {
                'augment': command_config['augment'],
                'relay': command_config['relay']
            }
        
        if 'augment' in command_config:
            return {'augment': command_config['augment']}
        
        if 'relay' in command_config:
            return {'relay': command_config['relay']}
        
        # Conditional handlers
        if 'handlers' in command_config:
            template_processor = TemplateProcessor(context)
            
            for handler in command_config['handlers']:
                if 'default' in handler:
                    # Default handler (always matches)
                    return handler
                
                if 'when' in handler:
                    # Evaluate condition
                    condition = handler['when']
                    if template_processor.evaluate_condition(condition):
                        return handler
        
        return None
    
    def get_execution_plan(self, match_result: MatchResult) -> List[Dict[str, Any]]:
        """
        Get list of steps to execute from a match result.
        
        Args:
            match_result: Result from match()
        
        Returns:
            List of execution steps
        """
        if not match_result.matched:
            return []
        
        handler = match_result.handler
        steps = []
        
        # Handle different execution modes
        if 'execute' in handler:
            # Direct execution steps
            steps.extend(self._normalize_steps(handler['execute']))
        
        elif 'augment' in handler:
            # Augmentation mode
            augment = handler['augment']
            
            # Before steps
            if 'before' in augment:
                steps.extend(self._normalize_steps(augment['before']))
            
            # Relay to native command
            if 'relay' in augment:
                if augment['relay'] == 'native':
                    steps.append({
                        'subprocess': {
                            'cmd': match_result.context._build_relay_command().split()
                        }
                    })
            
            # After steps
            if 'after' in augment:
                steps.extend(self._normalize_steps(augment['after']))
        
        elif 'relay' in handler:
            # Simple relay
            if handler['relay'] == 'native':
                steps.append({
                    'subprocess': {
                        'cmd': match_result.context._build_relay_command().split()
                    }
                })
        
        return steps
    
    def _normalize_steps(self, steps: Any) -> List[Dict[str, Any]]:
        """
        Normalize steps to consistent format.
        
        Handles both list and single step formats.
        """
        if not steps:
            return []
        
        if not isinstance(steps, list):
            steps = [steps]
        
        normalized = []
        for step in steps:
            if isinstance(step, str):
                # Assume shell command
                normalized.append({'shell': step})
            elif isinstance(step, dict):
                normalized.append(step)
        
        return normalized


