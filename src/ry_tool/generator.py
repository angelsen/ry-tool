"""
Command generator - orchestrates the pipeline from YAML to shell commands.
Single responsibility: coordinate the transformation pipeline.
"""
from typing import Any, Dict, List
from .pipeline import PipelineContext, PipeMode
from .normalizer import Normalizer
from .executors import registry


class CommandGenerator:
    """Orchestrate command generation from YAML config."""
    
    def __init__(self, config: Dict[str, Any], args: List[str], processor=None):
        self.config = config
        self.args = args
        self.processor = processor
        self.normalizer = Normalizer()
    
    def generate(self) -> str:
        """Generate shell commands from config."""
        # Identify structure and extract steps
        if 'pipeline' in self.config:
            return self._handle_pipeline(self.config['pipeline'])
        
        elif 'parallel' in self.config:
            return self._handle_parallel(self.config['parallel'])
        
        elif 'steps' in self.config:
            return self._handle_steps(self.config['steps'])
        
        elif 'match' in self.config:
            return self._handle_match(self.config['match'])
        
        else:
            # Single step
            return self._handle_single(self.config)
    
    def _handle_pipeline(self, config: Any) -> str:
        """Handle explicit pipeline structure."""
        # Extract steps
        if isinstance(config, list):
            steps = config
        else:
            steps = config.get('steps', [])
        
        # Process through pipeline
        context = PipelineContext(steps, PipeMode.PIPELINE)
        return self._process_steps(context)
    
    def _handle_parallel(self, config: Any) -> str:
        """Handle parallel execution."""
        # Extract steps
        if isinstance(config, list):
            steps = config
        else:
            steps = config.get('steps', [])
        
        # Process as parallel
        context = PipelineContext(steps, PipeMode.PARALLEL)
        return self._process_steps(context)
    
    def _handle_steps(self, steps: List[Any]) -> str:
        """Handle sequential steps."""
        context = PipelineContext(steps, PipeMode.SEQUENCE)
        return self._process_steps(context)
    
    def _handle_match(self, patterns: Dict[str, Any]) -> str:
        """Handle pattern matching."""
        # Find matching pattern
        matched = None
        
        for pattern, action in patterns.items():
            if pattern in ['default', '*']:
                continue
            
            # Simple matching for now
            if self.args and pattern == self.args[0]:
                matched = action
                break
        
        # Use default if no match
        if matched is None:
            matched = patterns.get('default') or patterns.get('*')
        
        if matched is None:
            return ""
        
        # Process matched action
        if isinstance(matched, list):
            return self._handle_steps(matched)
        else:
            return self._handle_single(matched)
    
    def _handle_single(self, step: Any) -> str:
        """Handle a single step."""
        steps = [step]
        context = PipelineContext(steps, PipeMode.SEQUENCE)
        return self._process_steps(context)
    
    def _process_steps(self, context: PipelineContext) -> str:
        """Process steps through the full pipeline."""
        # 1. Apply templates
        steps = context.steps
        if self.processor:
            steps = self.processor.process(steps)
        
        # 2. Normalize steps
        normalized = [self.normalizer.normalize_step(s) for s in steps]
        
        # 3. Compile each step
        commands = []
        for step in normalized:
            executor = registry.get(step['executor'])
            if executor:
                cmd = executor.compile(step['script'], step.get('config'))
                commands.append(cmd)
            else:
                commands.append(f"echo 'No executor: {step['executor']}' >&2")
        
        # 4. Join commands based on mode
        return self._join_commands(commands, context)
    
    def _join_commands(self, commands: List[str], context: PipelineContext) -> str:
        """Join commands according to context mode."""
        if not commands:
            return ""
        
        if len(commands) == 1:
            return commands[0]
        
        if context.mode == PipeMode.PIPELINE:
            # Join with pipes
            result = ' | \\\n'.join(commands)
            if context.fail_fast:
                result = "set -e; set -o pipefail\n" + result
            return result
        
        elif context.mode == PipeMode.PARALLEL:
            # Run in background
            result = []
            for cmd in commands:
                result.append(f"({cmd}) &")
            result.append("wait")
            return '\n'.join(result)
        
        else:  # SEQUENCE
            # Run sequentially
            if context.fail_fast:
                return "set -e\n" + '\n'.join(commands)
            return '\n'.join(commands)