"""
Context manager for detecting project types and environment details.
"""

import os
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class ProjectContext:
    type: str
    description: str
    risk_level: str  # low, medium, high
    files: List[str]

class ContextManager:
    """Detects project context and manages environment awareness."""
    
    def __init__(self):
        self.indicators = {
            "python": {
                "files": ["requirements.txt", "setup.py", "pyproject.toml", "Pipfile", "manage.py"],
                "desc": "Python Project",
                "risks": "Virtual environment activation, dependency conflicts"
            },
            "node": {
                "files": ["package.json", "yarn.lock", "pnpm-lock.yaml", "node_modules"],
                "desc": "Node.js Project",
                "risks": "Large node_modules, script execution permissions"
            },
            "rust": {
                "files": ["Cargo.toml", "Cargo.lock"],
                "desc": "Rust Project",
                "risks": "Compilation times, artifact sizes"
            },
            "git": {
                "files": [".git"],
                "desc": "Git Repository",
                "risks": "Uncommitted changes, branch divergence"
            },
            "docker": {
                "files": ["Dockerfile", "docker-compose.yml"],
                "desc": "Containerized Project",
                "risks": "Container state, port conflicts"
            }
        }

    def get_context(self, directory: str = ".") -> List[ProjectContext]:
        """
        Analyze the directory and return a list of detected contexts.
        """
        detected = []
        try:
            # List files in current directory (shallow)
            # Using os.listdir is faster/safer than walking for this purpose
            with os.scandir(directory) as entries:
                files = {entry.name for entry in entries}
        except OSError:
            return []

        for key, info in self.indicators.items():
            found_files = [f for f in info["files"] if f in files]
            if found_files:
                detected.append(ProjectContext(
                    type=key,
                    description=info["desc"],
                    risk_level="medium", # Default to medium for now
                    files=found_files
                ))
        
        return detected

    def get_file_list(self, directory: str = ".", limit: int = 50) -> str:
        """Return a comma-separated list of files in the directory."""
        try:
            files = sorted(os.listdir(directory))
            # Filter out hidden files/dirs for cleaner context, unless relevant
            visible_files = [f for f in files if not f.startswith('.')]
            
            if len(visible_files) > limit:
                return ", ".join(visible_files[:limit]) + f", ... ({len(visible_files)-limit} more)"
            return ", ".join(visible_files)
        except Exception:
            return "Unable to list files"

    def get_context_string(self) -> str:
        """Return a formatted string describing the current context."""
        cwd = os.getcwd()
        contexts = self.get_context(cwd)
        files_str = self.get_file_list(cwd)
        
        parts = []
        if contexts:
            desc = ", ".join([c.description for c in contexts])
            parts.append(f"Project: {desc}")
        else:
            parts.append("Project: Generic Directory")
            
        parts.append(f"Files: {files_str}")
        
        return "\n".join(parts)
