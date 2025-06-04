"""Main CLI application."""

import os
import sys
from typing import List

import typer
from rich.console import Console
from rich.prompt import Confirm
from dotenv import load_dotenv

from .ai import AIClient
from .commands import CommandExecutor, CommandResult, CommandGenerator, CommandSafetyChecker
from .files import FileEditor
from .system import SystemInfo
from .ui import DisplayManager

# Load environment variables
load_dotenv()

# Initialize Typer app and Rich console
app = typer.Typer()
console = Console()


class GhostApp:
    """Main Ghost application orchestrator."""
    
    def __init__(self):
        """Initialize the Ghost application."""
        self.console = console
        self.display = DisplayManager(console)
        
        # Initialize AI client
        try:
            self.ai_client = AIClient()
        except ValueError as e:
            self.display.show_error(str(e))
            sys.exit(1)
        
        # Initialize components
        self.command_generator = CommandGenerator(self.ai_client)
        self.file_editor = FileEditor(self.ai_client, console)
        self.command_executor = CommandExecutor()
        self.safety_checker = CommandSafetyChecker()

    def run(
        self,
        prompt: str,
        verbose: bool = False,
        dry_run: bool = False,
        force: bool = False,
        retry: bool = True,
        max_commands: int = 5
    ):
        """Run the main Ghost application logic."""
        # Get system information
        system_info = SystemInfo.get_current()
        command_history: List[CommandResult] = []
        
        self.display.show_header(prompt)
        
        if verbose:
            self.display.show_system_info(system_info)

        # Main command execution loop
        while len(command_history) < max_commands:
            # Get next command with spinner
            with self.display.show_spinner("AI is generating command", "dots12", show_completion=False):
                command = self.command_generator.generate_command(prompt, system_info, command_history)
            
            # Check if this is a file editing command
            is_edit, filename = self.safety_checker.is_file_edit_command(command)
            if is_edit and filename:
                if self._handle_file_edit(command, filename, prompt, system_info):
                    # Add synthetic command to history for file edit
                    command_history.append(CommandResult(
                        command=f"Interactive edit: {filename}",
                        stdout=f"File '{filename}' created/modified successfully",
                        stderr="",
                        returncode=0
                    ))
                    self.display.show_success(f"File editing completed for {filename}")
                else:
                    self.display.show_warning(f"File editing cancelled for {filename}")
                # File editing is complete, break out of the command loop
                break
            
            # Check command safety
            if not self._check_command_safety(command, force):
                break

            self.display.show_command(command, len(command_history) + 1)
            
            if dry_run:
                self.display.show_dry_run_mode()
                break
            
            # Execute the command
            result = self._execute_command(command, is_edit)
            command_history.append(result)
            
            # Show results
            self.display.show_command_results(result, verbose)
            
            # Handle retries if command failed
            if not result.success and retry:
                if self._attempt_retry(command, prompt, system_info, command_history, force):
                    # Update the last result with the retry result
                    pass  # The retry logic updates the history in place
            
            # Check if we should continue (skip for file operations)
            if not is_edit:
                with self.display.show_spinner("AI is analyzing progress", "dots6", show_completion=False):
                    should_continue_flag, reason = self.command_generator.should_continue(prompt, command_history, system_info)
                
                if not should_continue_flag:
                    if verbose:
                        self.display.show_info(f"Stopping: {reason}")
                    break
        
        # Show final results
        self._show_final_results(prompt, command_history, system_info, verbose)

    def _handle_file_edit(self, command: str, filename: str, prompt: str, system_info: SystemInfo) -> bool:
        """Handle file editing operations."""
        self.display.show_file_edit_detected(command)
        
        if Confirm.ask(f"Would you like to use interactive editing mode for '{filename}'?", default=True):
            return self.file_editor.interactive_edit(prompt, filename, system_info)
        else:
            self.display.show_info("Continuing with normal command execution...")
            return False

    def _check_command_safety(self, command: str, force: bool) -> bool:
        """Check if command is safe to execute."""
        if self.safety_checker.is_potentially_dangerous(command) and not force:
            self.display.show_dangerous_command_warning(command)
            if not Confirm.ask("This command could be harmful. Do you want to proceed?"):
                self.display.show_cancelled("Command execution")
                return False
        return True

    def _execute_command(self, command: str, is_file_edit: bool) -> CommandResult:
        """Execute a command with appropriate timeout settings."""
        # Use fancy spinner during command execution
        spinner_message = "Executing command" if not is_file_edit else "Processing file operation"
        spinner_style = "dots" if not is_file_edit else "arc"
        
        with self.display.show_spinner(spinner_message, spinner_style, show_completion=False):
            if is_file_edit:
                return self.command_executor.execute_no_timeout(command)
            else:
                return self.command_executor.execute(command)

    def _attempt_retry(
        self, 
        failed_command: str, 
        prompt: str, 
        system_info: SystemInfo, 
        command_history: List[CommandResult],
        force: bool
    ) -> bool:
        """Attempt to retry with an alternative command."""
        self.display.show_command_failed_retry()
        
        # Get alternative command with spinner
        with self.display.show_spinner("AI is finding alternative", "dots10"):
            alt_command = self.command_generator.generate_command(
                prompt, system_info, command_history, failed_command
            )
        
        if alt_command != failed_command:  # Only retry if we got a different command
            self.display.show_alternative_command(alt_command)
            
            # Check safety again
            if not self._check_command_safety(alt_command, force):
                return False
            
            # Check if alternative is also a file edit command
            alt_is_edit, _ = self.safety_checker.is_file_edit_command(alt_command)
            alt_result = self._execute_command(alt_command, alt_is_edit)
            
            # Replace the failed command with the alternative
            command_history[-1] = alt_result
            
            # Show alternative results
            self.display.show_command_results(alt_result, verbose=True)
            return True
        
        return False

    def _show_final_results(
        self, 
        prompt: str, 
        command_history: List[CommandResult], 
        system_info: SystemInfo, 
        verbose: bool
    ):
        """Show the final results and explanation."""
        if command_history:
            with self.display.show_spinner("AI is summarizing results", "dots8", show_completion=False):
                explanation = self.command_generator.generate_explanation(
                    prompt, command_history, system_info, verbose
                )
            self.display.show_final_results(explanation, command_history)
        else:
            self.display.show_no_commands_executed()


@app.command()
def main(
    prompt: str,
    verbose: bool = typer.Option(
        False,
        "--verbose", "-v",
        help="Show detailed command outputs"
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run", "-n",
        help="Show the command without executing it"
    ),
    force: bool = typer.Option(
        False,
        "--force", "-f",
        help="Execute potentially dangerous commands without confirmation"
    ),
    retry: bool = typer.Option(
        True,
        "--retry/--no-retry",
        help="Retry with a different command if the first one fails"
    ),
    max_commands: int = typer.Option(
        5,
        "--max-commands",
        help="Maximum number of commands to execute"
    )
):
    """
    Execute commands based on natural language prompts using AI.
    """
    ghost_app = GhostApp()
    ghost_app.run(prompt, verbose, dry_run, force, retry, max_commands) 