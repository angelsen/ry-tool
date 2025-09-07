"""
Command generator - orchestrates the pipeline from YAML to shell commands.
Single responsibility: coordinate the transformation pipeline.
"""

from typing import Any, Dict, List
from .pipeline import PipelineContext, PipeMode
from .normalizer import Normalizer
from .executors import registry
from .context import ExecutionContext


class CommandGenerator:
    """Orchestrate command generation from YAML config."""

    def __init__(self, config: Dict[str, Any], context: ExecutionContext, processor=None):
        self.config = config
        self.context = context
        self.processor = processor
        self.normalizer = Normalizer()

    def generate(self) -> str:
        """Generate shell commands from config."""
        # Get environment exports from context
        env_commands = self.context.get_env_exports()
        
        # Add env section from config if present
        if "env" in self.config:
            for key, value in self.config["env"].items():
                # Process templates in env values
                if self.processor:
                    value = self.processor.process(value)
                env_commands.append(f"export {key}={value}")

        # Identify structure and extract steps
        main_commands = ""
        if "pipeline" in self.config:
            main_commands = self._handle_pipeline(self.config["pipeline"])

        elif "parallel" in self.config:
            main_commands = self._handle_parallel(self.config["parallel"])

        elif "steps" in self.config:
            main_commands = self._handle_steps(self.config["steps"])

        elif "match" in self.config:
            main_commands = self._handle_match(self.config["match"])

        elif "if" in self.config:
            main_commands = self._handle_conditional(self.config)

        elif "foreach" in self.config:
            main_commands = self._handle_foreach(self.config)

        else:
            # Single step
            main_commands = self._handle_single(self.config)

        # Combine env and main commands
        if env_commands:
            return "\n".join(env_commands) + "\n" + main_commands
        return main_commands

    def _handle_pipeline(self, config: Any) -> str:
        """Handle explicit pipeline structure."""
        # Extract steps
        if isinstance(config, list):
            steps = config
        else:
            steps = config.get("steps", [])

        # Process through pipeline
        context = PipelineContext(steps, PipeMode.PIPELINE)
        return self._process_steps(context)

    def _handle_parallel(self, config: Any) -> str:
        """Handle parallel execution."""
        # Extract steps
        if isinstance(config, list):
            steps = config
        else:
            steps = config.get("steps", [])

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

        # Sort patterns by length (longest first) to match more specific patterns first
        sorted_patterns = sorted(patterns.items(), 
                                key=lambda x: len(x[0].split()), 
                                reverse=True)
        
        for pattern, action in sorted_patterns:
            if pattern in ["default", "*"]:
                continue

            # Check if pattern matches arguments
            if self.context.args:
                if " " in pattern:
                    # Multi-word pattern: split and check if args starts with it
                    pattern_parts = pattern.split()
                    if len(self.context.args) >= len(pattern_parts):
                        if self.context.args[:len(pattern_parts)] == pattern_parts:
                            matched = action
                            break
                else:
                    # Single word pattern: original behavior
                    if pattern == self.context.args[0]:
                        matched = action
                        break

        # Use default if no match
        if matched is None:
            matched = patterns.get("default") or patterns.get("*")

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

    def _handle_conditional(self, config: Dict[str, Any]) -> str:
        """Handle if/then/else structure."""
        condition = config.get("if", "")
        then_steps = config.get("then", [])
        else_steps = config.get("else", [])

        # Process condition template
        if self.processor:
            condition = self.processor.process(condition)

        # Build conditional command
        commands = []
        commands.append(f"if {condition}; then")

        # Process then branch
        if then_steps:
            if isinstance(then_steps, list):
                then_cmd = self._handle_steps(then_steps)
            else:
                then_cmd = self._handle_single(then_steps)
            # Indent then commands
            for line in then_cmd.split("\n"):
                commands.append(f"  {line}")

        # Process else branch if present
        if else_steps:
            commands.append("else")
            if isinstance(else_steps, list):
                else_cmd = self._handle_steps(else_steps)
            else:
                else_cmd = self._handle_single(else_steps)
            # Indent else commands
            for line in else_cmd.split("\n"):
                commands.append(f"  {line}")

        commands.append("fi")
        return "\n".join(commands)

    def _handle_foreach(self, config: Dict[str, Any]) -> str:
        """Handle foreach loop structure."""
        items = config.get("items", [])
        var = config.get("var", "item")
        do_steps = config.get("do", [])

        # Process items template if string
        if isinstance(items, str) and self.processor:
            items = self.processor.process(items)

        # Build loop command
        commands = []
        if isinstance(items, list):
            # Static list of items
            items_str = " ".join(f'"{item}"' for item in items)
            commands.append(f"for {var} in {items_str}; do")
        else:
            # Dynamic items (e.g., glob or command output)
            commands.append(f"for {var} in {items}; do")

        # Process loop body
        if do_steps:
            if isinstance(do_steps, list):
                do_cmd = self._handle_steps(do_steps)
            else:
                do_cmd = self._handle_single(do_steps)
            # Indent loop commands
            for line in do_cmd.split("\n"):
                commands.append(f"  {line}")

        commands.append("done")
        return "\n".join(commands)

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
            executor = registry.get(step["executor"])
            if executor:
                cmd = executor.compile(step["script"], step.get("config"))

                # Handle test condition
                if "test" in step:
                    test_cmd = f"if {step['test']}; then {cmd}; "
                    if "fail" in step:
                        test_cmd += f"else echo '{step['fail']}' >&2; exit 1; "
                    test_cmd += "fi"
                    cmd = test_cmd

                # Handle capture directive
                if "capture" in step:
                    cmd = f"export {step['capture']}=$({cmd})"

                commands.append(cmd)
            else:
                commands.append(
                    f"echo 'ERROR: No executor for {step.get('executor')}' >&2; exit 1"
                )

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
            result = " | \\\n".join(commands)
            if context.fail_fast:
                result = "set -e; set -o pipefail\n" + result
            return result

        elif context.mode == PipeMode.PARALLEL:
            # Run in background
            result = []
            for cmd in commands:
                result.append(f"({cmd}) &")
            result.append("wait")
            return "\n".join(result)

        else:  # SEQUENCE
            # Run sequentially
            if context.fail_fast:
                return "set -e\n" + "\n".join(commands)
            return "\n".join(commands)
