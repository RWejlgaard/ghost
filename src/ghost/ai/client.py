"""OpenAI client wrapper."""

import os
from typing import List, Dict, Optional
from openai import OpenAI


class AIClient:
    """Wrapper for OpenAI client with ghost-specific functionality."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the AI client."""
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required")
        
        self.client = OpenAI(api_key=self.api_key)

    def generate_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = "gpt-4o-mini",
        temperature: float = 0.3,
        max_tokens: int = 150
    ) -> str:
        """Generate a completion from the AI model."""
        response = self.client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        content = response.choices[0].message.content.strip()
        return self._clean_response(content)
    
    def _clean_response(self, content: str) -> str:
        """Clean up AI response content."""
        # Remove common unwanted formatting
        content = content.replace('{{response_code}}', '')
        content = content.replace('{{', '')
        content = content.replace('}}', '')
        content = content.replace('<placeholder>', '')
        content = content.replace('```', '')  # Remove markdown code blocks
        content = content.replace('`', '').replace('"', '').replace("'", "").strip()
        
        # Remove common markdown language indicators at the start
        lines = content.split('\n')
        if lines and lines[0].strip().lower() in ['python', 'javascript', 'bash', 'html', 'css', 'json', 'yaml', 'sh']:
            lines = lines[1:]
            content = '\n'.join(lines)
        
        return content.strip() 