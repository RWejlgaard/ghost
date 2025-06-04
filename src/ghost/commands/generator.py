"""Command generation using AI."""

from typing import List, Optional, Tuple
from ..ai import AIClient, PromptTemplates
from ..system import SystemInfo
from .executor import CommandResult


class CommandGenerator:
    """Generates shell commands using AI."""
    
    def __init__(self, ai_client: AIClient):
        """Initialize the command generator."""
        self.ai_client = ai_client

    def generate_command(
        self,
        prompt: str,
        system_info: SystemInfo,
        command_history: Optional[List[CommandResult]] = None,
        previous_attempt: Optional[str] = None
    ) -> str:
        """Generate a shell command based on natural language prompt."""
        
        system_prompt = PromptTemplates.command_generation(system_info)
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
        
        # Add command history context if available
        if command_history:
            history_text = self._format_command_history(command_history)
            messages.append({"role": "user", "content": history_text})
        
        if previous_attempt:
            messages.append({
                "role": "user", 
                "content": f"Previous command failed: {previous_attempt}\nPlease suggest a better alternative."
            })

        return self.ai_client.generate_completion(messages)

    def should_continue(
        self,
        prompt: str,
        command_history: List[CommandResult],
        system_info: SystemInfo
    ) -> Tuple[bool, str]:
        """Determine if more commands are needed to fully answer the request."""
        
        if not command_history:
            return True, "No commands executed yet"
        
        # Don't continue if we've run too many commands
        if len(command_history) >= 5:
            return False, "Maximum number of commands reached"
        
        # Check if the last command failed catastrophically
        last_result = command_history[-1]
        if (not last_result.success and 
            not last_result.stdout and 
            "permission denied" in last_result.stderr.lower()):
            return False, "Permission denied - cannot continue"
        
        system_prompt = PromptTemplates.continuation_analysis(system_info)
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Original request: {prompt}\n\nCommands executed so far:"}
        ]
        
        for i, result in enumerate(command_history, 1):
            status = "successful" if result.success else "failed"
            messages.append({
                "role": "user", 
                "content": f"Command {i}: {result.command} ({status})\nOutput: {result.stdout[:300] if result.stdout else '(no output)'}\nErrors: {result.stderr[:200] if result.stderr else '(no errors)'}"
            })
        
        messages.append({
            "role": "user",
            "content": "Do we have enough information to answer the original request, or should we continue with more commands?"
        })

        decision = self.ai_client.generate_completion(messages, max_tokens=50)
        should_continue_flag = decision.upper().startswith("CONTINUE")
        
        return should_continue_flag, decision

    def generate_explanation(
        self,
        prompt: str,
        command_history: List[CommandResult],
        system_info: SystemInfo,
        verbose: bool = False
    ) -> str:
        """Generate explanation of what was accomplished."""
        
        system_prompt = PromptTemplates.explanation_generation(system_info, verbose)
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Original request: {prompt}\n\nCommands executed:"}
        ]
        
        for i, result in enumerate(command_history, 1):
            status = "successful" if result.success else "failed"
            messages.append({
                "role": "user", 
                "content": f"Command {i}: {result.command} ({status})\nOutput: {result.stdout if result.stdout else '(no output)'}\nErrors: {result.stderr if result.stderr else '(no errors)'}"
            })
        
        explanation_prompt = ("Please provide a detailed explanation of what was accomplished and what the results mean." 
                            if verbose else 
                            "Please provide a concise summary answering the original request.")
        
        messages.append({"role": "user", "content": explanation_prompt})

        max_tokens = 400 if verbose else 150
        return self.ai_client.generate_completion(messages, max_tokens=max_tokens)

    def _format_command_history(self, command_history: List[CommandResult]) -> str:
        """Format command history for inclusion in prompts."""
        history_text = "Previous commands executed:\n"
        for i, result in enumerate(command_history, 1):
            status = "SUCCESS" if result.success else "FAILED"
            history_text += f"{i}. {result.command} [{status}]\n"
            if result.stdout:
                history_text += f"   Output: {result.stdout[:200]}{'...' if len(result.stdout) > 200 else ''}\n"
            if result.stderr:
                history_text += f"   Error: {result.stderr[:100]}{'...' if len(result.stderr) > 100 else ''}\n"
        
        return history_text 