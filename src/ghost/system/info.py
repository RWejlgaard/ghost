"""System information utilities."""

import os
import platform
from typing import Dict
from dataclasses import dataclass


@dataclass
class SystemInfo:
    """System information container."""
    os: str
    release: str
    machine: str
    shell: str
    cwd: str

    @classmethod
    def get_current(cls) -> "SystemInfo":
        """Get current system information."""
        system = platform.system()
        release = platform.release()
        machine = platform.machine()
        shell = os.environ.get('SHELL', '/bin/bash')
        cwd = os.getcwd()
        
        return cls(
            os=system,
            release=release,
            machine=machine,
            shell=shell,
            cwd=cwd
        )

    def to_dict(self) -> Dict[str, str]:
        """Convert to dictionary format."""
        return {
            "os": self.os,
            "release": self.release,
            "machine": self.machine,
            "shell": self.shell,
            "cwd": self.cwd
        } 