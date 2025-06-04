"""File editing with AI assistance."""

import difflib
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.prompt import Confirm, Prompt
from rich.panel import Panel
from rich.syntax import Syntax

from ..ai import AIClient, PromptTemplates
from ..system import SystemInfo


class FileEditor:
    """Interactive file editor with AI assistance."""
    
    def __init__(self, ai_client: AIClient, console: Console):
        """Initialize the file editor."""
        self.ai_client = ai_client
        self.console = console

    def interactive_edit(self, prompt: str, filename: str, system_info: SystemInfo) -> bool:
        """Interactive file editing mode with AI assistance."""
        self.console.print(f"\n[bold blue]Entering interactive file editing mode for:[/bold blue] {filename}")
        
        # Check if file exists
        file_path = Path(filename)
        current_content = ""
        
        if file_path.exists():
            try:
                current_content = file_path.read_text()
                self.console.print(f"[green]Found existing file[/green]")
                self._show_file_content(current_content, filename)
            except Exception as e:
                self.console.print(f"[red]Error reading file: {e}[/red]")
                return False
        else:
            self.console.print(f"[yellow]Creating new file[/yellow]")
        
        # Generate initial content
        if not current_content:
            self.console.print("[dim]Generating initial content...[/dim]")
            new_content = self._generate_file_content(prompt, filename, current_content, system_info)
            self._show_file_content(new_content, filename)
            current_content = new_content
        
        # Interactive editing loop
        while True:
            self.console.print("\n[bold]What would you like to do?[/bold]")
            self.console.print("1. Save and exit")
            self.console.print("2. Make changes")
            self.console.print("3. View current content")
            self.console.print("4. Exit without saving")
            
            choice = Prompt.ask("Choose an option", choices=["1", "2", "3", "4"], default="1")
            
            if choice == "1":
                return self._save_file(file_path, current_content, filename)
            
            elif choice == "2":
                current_content = self._make_changes(current_content, filename)
            
            elif choice == "3":
                self._show_file_content(current_content, filename)
            
            elif choice == "4":
                return self._exit_without_saving()

    def _generate_file_content(self, prompt: str, filename: str, current_content: str, system_info: SystemInfo) -> str:
        """Generate file content using AI."""
        system_prompt = PromptTemplates.file_content_generation(system_info, filename, current_content)
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]

        return self.ai_client.generate_completion(messages, max_tokens=2000)

    def _modify_file_content(self, current_content: str, modification_request: str, filename: str) -> str:
        """Modify existing file content based on user request."""
        system_prompt = PromptTemplates.file_modification(filename, current_content)
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": modification_request}
        ]

        return self.ai_client.generate_completion(messages, max_tokens=2000)

    def _make_changes(self, current_content: str, filename: str) -> str:
        """Handle the change-making process."""
        modification = Prompt.ask("\n[bold]What changes would you like to make?[/bold]")
        self.console.print("[dim]Applying changes...[/dim]")
        
        old_content = current_content
        new_content = self._modify_file_content(current_content, modification, filename)
        
        if new_content != old_content:
            self._show_file_diff(old_content, new_content, filename)
            
            if Confirm.ask("Apply these changes?", default=True):
                self.console.print("[green]Changes applied[/green]")
                return new_content
            else:
                self.console.print("[yellow]Changes discarded[/yellow]")
                return current_content
        else:
            self.console.print("[dim]No changes were made[/dim]")
            return current_content

    def _save_file(self, file_path: Path, content: str, filename: str) -> bool:
        """Save the file content."""
        try:
            # Create directory if it doesn't exist
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content)
            self.console.print(f"[green]File saved successfully: {filename}[/green]")
            return True
        except Exception as e:
            self.console.print(f"[red]Error saving file: {e}[/red]")
            if Confirm.ask("Try again?"):
                return self._save_file(file_path, content, filename)
            return False

    def _exit_without_saving(self) -> bool:
        """Handle exiting without saving."""
        if Confirm.ask("Are you sure you want to exit without saving?"):
            self.console.print("[yellow]Exited without saving[/yellow]")
            return False
        return True  # Continue editing

    def _show_file_diff(self, old_content: str, new_content: str, filename: str):
        """Show a diff between old and new file content."""
        old_lines = old_content.splitlines(keepends=True) if old_content else []
        new_lines = new_content.splitlines(keepends=True)
        
        diff = list(difflib.unified_diff(
            old_lines, 
            new_lines, 
            fromfile=f"a/{filename}", 
            tofile=f"b/{filename}",
            lineterm=""
        ))
        
        if diff:
            diff_text = ''.join(diff)
            self.console.print(Panel(diff_text, title="Changes", border_style="yellow"))
        else:
            self.console.print("[dim]No changes detected[/dim]")

    def _show_file_content(self, content: str, filename: str):
        """Display file content with syntax highlighting."""
        # Try to detect language from file extension
        extension = Path(filename).suffix.lower()
        language_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.html': 'html',
            '.css': 'css',
            '.json': 'json',
            '.yaml': 'yaml',
            '.yml': 'yaml',
            '.sh': 'bash',
            '.md': 'markdown',
            '.sql': 'sql',
            '.xml': 'xml',
            '.toml': 'toml',
            '.ini': 'ini',
            '.conf': 'ini',
            '.txt': 'text'
        }
        
        language = language_map.get(extension, 'text')
        
        try:
            syntax = Syntax(content, language, theme="monokai", line_numbers=True)
            self.console.print(Panel(syntax, title=f"{filename}", border_style="blue"))
        except:
            # Fallback to plain text if syntax highlighting fails
            self.console.print(Panel(content, title=f"{filename}", border_style="blue")) 