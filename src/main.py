#!/usr/bin/env python3
import os
import subprocess
import sys
from typing import Optional, List, Tuple

import typer
from rich.console import Console
from rich.prompt import Confirm
from rich.panel import Panel
from openai import OpenAI
from dotenv import load_dotenv

# Initialize Typer app and Rich console
app = typer.Typer()
console = Console()

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_command_from_ai(prompt: str, command_history: List[Tuple[str, str]] = None, force: bool = False) -> Tuple[str, bool]:
    """Get a shell command from OpenAI based on the prompt and command history.
    Returns a tuple of (command, is_unsafe)"""
    messages = [
        {"role": "system", "content": """You are an AI that converts natural language prompts into shell commands.
        - ONLY return the command, nothing else
        - DO NOT include any explanations
        - DO NOT use markdown formatting
        - If you think a command might be destructive, prefix it with 'UNSAFE:'
        - Prefer common Unix commands that are likely to be available
        - Never include rm -rf / or similar dangerous commands"""},
        {"role": "user", "content": prompt}
    ]

    # Add command history context if available
    if command_history:
        history_prompt = "Previous commands and their outputs:\n"
        for cmd, output in command_history:
            history_prompt += f"Command: {cmd}\nOutput: {output}\n"
        messages.append({"role": "user", "content": history_prompt})

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.7,
        max_tokens=100
    )

    command = response.choices[0].message.content.strip()
    is_unsafe = command.startswith("UNSAFE:")
    
    if is_unsafe:
        # Extract the actual command
        command = command[7:].strip()
    
    return command, is_unsafe

def get_final_response(prompt: str, command_history: List[Tuple[str, str]]) -> str:
    """Get a final human-friendly response from OpenAI based on the command history."""
    messages = [
        {"role": "system", "content": """You are a helpful AI assistant that explains command results.
        Provide a clear, concise explanation of what was found or done.
        If there were any errors or issues, explain them clearly."""},
        {"role": "user", "content": f"Original request: {prompt}\n\nCommand history and outputs:"}
    ]

    for cmd, output in command_history:
        messages.append({"role": "user", "content": f"Command: {cmd}\nOutput: {output}"})

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.7,
        max_tokens=300
    )

    return response.choices[0].message.content.strip()

def execute_command(command: str) -> str:
    """Execute a shell command and return its output."""
    try:
        result = subprocess.run(
            command,
            shell=True,
            text=True,
            capture_output=True,
            timeout=30
        )
        return result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        return "Command timed out after 30 seconds"
    except Exception as e:
        return f"Error executing command: {str(e)}"

@app.command()
def main(
    prompt: str,
    verbose: bool = typer.Option(
        False,
        "--verbose", "-v",
        help="Show detailed command outputs"
    ),
    force: bool = typer.Option(
        False,
        "--force", "-f",
        help="Execute unsafe commands without confirmation"
    )
):
    """
    Execute commands based on natural language prompts using AI.
    """
    if not os.getenv("OPENAI_API_KEY"):
        console.print("[red]Error: OPENAI_API_KEY not found in environment variables[/red]")
        sys.exit(1)

    command_history = []
    max_iterations = 3
    iteration = 0

    console.print(Panel.fit(f"[bold blue]Processing request:[/bold blue] {prompt}", title="👻 Ghost"))

    while iteration < max_iterations:
        # Get command from AI
        command, is_unsafe = get_command_from_ai(prompt, command_history, force)
        
        if is_unsafe:
            console.print(f"[yellow]Warning: The following command was deemed unsafe:[/yellow]")
            console.print(f"[bold yellow]{command}[/bold yellow]")
            if not force and not Confirm.ask("Do you want to proceed anyway?"):
                console.print("[red]Command execution cancelled[/red]")
                break
            # Get the actual command after confirmation
            command, _ = get_command_from_ai(prompt, command_history, force=True)

        # Show and execute command
        console.print(f"\n[bold yellow]Command {iteration + 1}:[/bold yellow] {command}")
        console.print("[dim]Executing...[/dim]")
        output = execute_command(command)
        command_history.append((command, output))
        
        # Show output in a panel if verbose mode is enabled
        if verbose:
            console.print(Panel(output, title=f"Output {iteration + 1}", border_style="dim"))
        
        # Check if we need another iteration
        if iteration < max_iterations - 1:
            next_command, is_unsafe = get_command_from_ai(
                f"Based on the output of '{command}', do we need another command to fulfill the original request: '{prompt}'? If yes, what should it be? If no, return 'DONE'",
                command_history,
                force
            )
            if next_command == "DONE":
                break
            if is_unsafe:
                console.print(f"[yellow]Warning: The following command was deemed unsafe:[/yellow]")
                console.print(f"[bold yellow]{next_command}[/bold yellow]")
                if not force and not Confirm.ask("Do you want to proceed anyway?"):
                    console.print("[red]Command execution cancelled[/red]")
                    break
                # Get the actual command after confirmation
                next_command, _ = get_command_from_ai(
                    f"Based on the output of '{command}', do we need another command to fulfill the original request: '{prompt}'? If yes, what should it be? If no, return 'DONE'",
                    command_history,
                    force=True
                )
            command = next_command
        
        iteration += 1

    # Get final response
    if command_history:
        final_response = get_final_response(prompt, command_history)
        console.print(Panel(final_response, title="[bold green]Final Response[/bold green]", border_style="green"))
    else:
        console.print("[red]No commands were executed.[/red]")

if __name__ == "__main__":
    app()
