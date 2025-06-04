"""Command execution utilities."""

import subprocess
from typing import Tuple, NamedTuple
from dataclasses import dataclass


@dataclass
class CommandResult:
    """Result of a command execution."""
    command: str
    stdout: str
    stderr: str
    returncode: int
    
    @property
    def success(self) -> bool:
        """Check if command was successful."""
        return self.returncode == 0


class CommandExecutor:
    """Handles shell command execution."""
    
    DEFAULT_TIMEOUT = 30
    
    @classmethod
    def execute(cls, command: str, timeout: int = None) -> CommandResult:
        """Execute a shell command with timeout."""
        timeout = timeout or cls.DEFAULT_TIMEOUT
        
        try:
            result = subprocess.run(
                command,
                shell=True,
                text=True,
                capture_output=True,
                timeout=timeout
            )
            return CommandResult(
                command=command,
                stdout=result.stdout,
                stderr=result.stderr,
                returncode=result.returncode
            )
        except subprocess.TimeoutExpired:
            return CommandResult(
                command=command,
                stdout="",
                stderr=f"Command timed out after {timeout} seconds",
                returncode=1
            )
        except Exception as e:
            return CommandResult(
                command=command,
                stdout="",
                stderr=f"Error executing command: {str(e)}",
                returncode=1
            )

    @classmethod
    def execute_no_timeout(cls, command: str) -> CommandResult:
        """Execute a shell command without timeout (for file operations)."""
        try:
            result = subprocess.run(
                command,
                shell=True,
                text=True,
                capture_output=True
            )
            return CommandResult(
                command=command,
                stdout=result.stdout,
                stderr=result.stderr,
                returncode=result.returncode
            )
        except Exception as e:
            return CommandResult(
                command=command,
                stdout="",
                stderr=f"Error executing command: {str(e)}",
                returncode=1
            ) 