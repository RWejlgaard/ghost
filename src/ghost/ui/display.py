"""UI display utilities using Rich."""

import time
from typing import List
from contextlib import contextmanager
from rich.console import Console
from rich.spinner import Spinner
from rich.panel import Panel
from rich.table import Table
from rich.live import Live
from rich.text import Text
from rich.columns import Columns

from ..commands import CommandResult
from ..system import SystemInfo


class DisplayManager:
    """Manages UI display using Rich console."""
    
    def __init__(self, console: Console):
        """Initialize the display manager."""
        self.console = console

    def show_header(self, prompt: str):
        """Show the application header with the user's request."""
        self.console.print(Panel.fit(f"[bold blue]Processing request:[/bold blue] {prompt}", title="Ghost"))

    def show_system_info(self, system_info: SystemInfo):
        """Display system information in a table."""
        table = Table(title="System Information")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="magenta")
        
        for key, value in system_info.to_dict().items():
            table.add_row(key.replace('_', ' ').title(), value)
        
        self.console.print(table)

    def show_command(self, command: str, command_number: int):
        """Display the command being executed."""
        self.console.print(f"\n[bold green]Command {command_number}:[/bold green] {command}")

    def show_command_results(self, result: CommandResult, verbose: bool = False):
        """Display command execution results."""
        if verbose or not result.success:
            if result.stdout:
                self.console.print(Panel(result.stdout, title="Output", border_style="green"))
            if result.stderr:
                self.console.print(Panel(result.stderr, title="Errors", border_style="red"))
            self.console.print(f"[dim]Exit code: {result.returncode}[/dim]")
        elif result.stdout:
            # In normal mode, show a brief preview of successful output
            preview = result.stdout[:100] + "..." if len(result.stdout) > 100 else result.stdout
            self.console.print(f"[dim]{preview}[/dim]")

    def show_alternative_command(self, command: str):
        """Display an alternative command being tried."""
        self.console.print(f"[bold green]Alternative command:[/bold green] {command}")

    def show_dangerous_command_warning(self, command: str):
        """Show warning for potentially dangerous commands."""
        self.console.print(f"[yellow]Potentially dangerous command detected:[/yellow]")
        self.console.print(f"[bold red]{command}[/bold red]")

    def show_file_edit_detected(self, command: str):
        """Show that a file editing command was detected."""
        self.console.print(f"\n[bold yellow]Detected file editing command:[/bold yellow] {command}")

    def show_final_results(self, explanation: str, command_history: List[CommandResult]):
        """Show the final results and explanation."""
        # Determine overall success
        overall_success = any(result.success for result in command_history)
        style = "green" if overall_success else "red"
        title = "[bold green]Results[/bold green]" if overall_success else "[bold red]Failed[/bold red]"
        self.console.print(Panel(explanation, title=title, border_style=style))

    def show_no_commands_executed(self):
        """Show message when no commands were executed."""
        self.console.print("[red]No commands were executed.[/red]")

    def show_error(self, message: str):
        """Show an error message."""
        self.console.print(f"[red]Error: {message}[/red]")

    def show_warning(self, message: str):
        """Show a warning message."""
        self.console.print(f"[yellow]{message}[/yellow]")

    def show_success(self, message: str):
        """Show a success message."""
        self.console.print(f"[green]{message}[/green]")

    def show_info(self, message: str):
        """Show an info message."""
        self.console.print(f"[dim]{message}[/dim]")

    def show_dry_run_mode(self):
        """Show dry run mode message."""
        self.console.print("[yellow]Dry run mode - command not executed[/yellow]")

    def show_command_failed_retry(self):
        """Show that command failed and retry is being attempted."""
        self.console.print("[yellow]Command failed. Trying alternative approach...[/yellow]")

    def show_cancelled(self, operation: str):
        """Show that an operation was cancelled."""
        self.console.print(f"[red]{operation} cancelled[/red]")

    @contextmanager
    def show_spinner(self, message: str = "Executing", spinner_style: str = "dots", show_completion: bool = True):
        """
        Context manager for showing a fancy loading spinner during command execution.
        Similar to npm's loading indicators.
        
        Args:
            message: The message to display alongside the spinner
            spinner_style: The spinner style to use ('dots', 'line', 'arc', 'arrow', etc.)
            show_completion: Whether to show a completion message when done
        """
        # Map different operations to different colors
        color_map = {
            "AI": "magenta",
            "Executing": "cyan", 
            "Processing": "yellow",
            "Finding": "blue",
            "Summarizing": "green"
        }
        
        # Determine color based on message content
        spinner_color = "cyan"  # default
        for key, color in color_map.items():
            if key.lower() in message.lower():
                spinner_color = color
                break
        
        # Create spinner with dynamic color
        spinner = Spinner(spinner_style, style=spinner_color, speed=1.2)
        
        # Create the display text with styling
        display_text = Text()
        display_text.append(message, style=spinner_color)
        display_text.append("...", style="dim")
        
        # Use Live to update the display
        with Live(
            console=self.console,
            auto_refresh=True,
            refresh_per_second=10,
            transient=not show_completion
        ) as live:
            # Create columns layout with spinner and text
            layout = Columns([spinner, display_text], padding=(0, 1))
            live.update(layout)
            
            try:
                yield
            finally:
                if show_completion:
                    # Show completion message briefly
                    completion_text = Text()
                    completion_text.append("Completed: ", style="green")
                    completion_text.append(message, style="dim")
                    live.update(completion_text)
                    # Brief pause to show completion
                    time.sleep(0.2)

    def show_ai_thinking(self):
        """Show that AI is processing the request."""
        return self.show_spinner("AI is thinking", "dots12")

    def show_executing(self):
        """Show that a command is being executed - deprecated, use show_spinner context manager instead."""
        self.console.print("[dim]Executing...[/dim]") 