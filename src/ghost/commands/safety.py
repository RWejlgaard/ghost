"""Command safety checking utilities."""

import re
from typing import Tuple, Optional


class CommandSafetyChecker:
    """Checks commands for potentially dangerous operations."""
    
    DANGEROUS_PATTERNS = [
        'rm -rf /',
        'rm -rf *',
        'dd if=',
        'mkfs.',
        'fdisk',
        'format',
        'del /s /q',
        'rmdir /s',
        'shutdown',
        'reboot',
        'halt',
        'init 0',
        'init 6',
        '> /dev/',
        'chmod -R 777 /',
        'chown -R',
        'find / -delete',
        'rm -rf ~',
        'rm -rf $HOME'
    ]
    
    FILE_EDIT_PATTERNS = [
        r'nano\s+(\S+)',
        r'vim?\s+(\S+)',
        r'emacs\s+(\S+)',
        r'code\s+(\S+)',
        r'touch\s+(\S+)',
        r'cat\s*>\s*(\S+)',
        r'echo\s+.*>\s*(\S+)',
        r'tee\s+(\S+)',
    ]

    @classmethod
    def is_potentially_dangerous(cls, command: str) -> bool:
        """Check if a command is potentially dangerous."""
        command_lower = command.lower()
        
        for pattern in cls.DANGEROUS_PATTERNS:
            if pattern in command_lower:
                return True
        
        # Check for suspicious redirects
        if any(redirect in command for redirect in ['> /', '>> /', '> /dev/', '>> /dev/']):
            return True
            
        return False

    @classmethod
    def is_file_edit_command(cls, command: str) -> Tuple[bool, Optional[str]]:
        """Check if command is for file creation/editing and extract filename."""
        command_lower = command.lower().strip()
        
        # Check file editing patterns
        for pattern in cls.FILE_EDIT_PATTERNS:
            match = re.search(pattern, command_lower)
            if match:
                filename = match.group(1).strip()
                filename = cls._clean_filename(filename)
                if filename:
                    return True, filename
        
        # Check for redirection to files
        if '>' in command and not any(dangerous in command for dangerous in ['> /', '> /dev/']):
            parts = command.split('>')
            if len(parts) >= 2:
                filename = parts[-1].strip()
                filename = cls._clean_filename(filename)
                if filename and not filename.startswith('/dev/'):
                    return True, filename
        
        return False, None

    @staticmethod
    def _clean_filename(filename: str) -> str:
        """Clean up filename from command parsing."""
        # Remove quotes and unwanted characters
        filename = filename.replace('"', '').replace("'", "").replace('`', '')
        filename = filename.replace('{{response_code}}', '').replace('{{', '').replace('}}', '')
        return filename.strip() 