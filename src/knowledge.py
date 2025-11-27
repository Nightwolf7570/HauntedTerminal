"""
Knowledge base manager for custom commands, paths, and examples.
"""

import os
from pathlib import Path
from typing import Dict, List, Optional


class KnowledgeBase:
    """Manages user-defined commands, paths, and examples."""
    
    def __init__(self, knowledge_file: Optional[str] = None):
        """
        Initialize knowledge base.
        
        Args:
            knowledge_file: Path to knowledge file. Defaults to ~/.haunted/knowledge.txt
        """
        if knowledge_file is None:
            home = Path.home()
            haunted_dir = home / ".haunted"
            haunted_dir.mkdir(exist_ok=True)
            self.knowledge_file = haunted_dir / "knowledge.txt"
        else:
            self.knowledge_file = Path(knowledge_file)
        
        # Create default knowledge file if it doesn't exist
        if not self.knowledge_file.exists():
            self._create_default_knowledge()
    
    def _create_default_knowledge(self):
        """Create a default knowledge file with examples."""
        default_content = """# Haunted Terminal Knowledge Base
# Add your custom commands, paths, and examples here
# Format: natural language -> shell command

# Application Paths
open cursor -> open -a "Cursor"
open vscode -> open -a "Visual Studio Code"
open chrome -> open -a "Google Chrome"
open finder -> open .

# Custom Directories
go to projects -> cd ~/Projects
go to downloads -> cd ~/Downloads
go to desktop -> cd ~/Desktop

# Custom Commands
# Add your frequently used commands here
# Example: backup my code -> rsync -av ~/Projects ~/Backup/

# Tips:
# - One command per line
# - Use -> to separate natural language from shell command
# - Lines starting with # are comments
# - Empty lines are ignored
"""
        self.knowledge_file.write_text(default_content)
    
    def load_knowledge(self) -> List[tuple[str, str]]:
        """
        Load knowledge from file.
        
        Returns:
            List of (natural_language, shell_command) tuples
        """
        if not self.knowledge_file.exists():
            return []
        
        knowledge = []
        try:
            content = self.knowledge_file.read_text()
            for line in content.split('\n'):
                line = line.strip()
                
                # Skip comments and empty lines
                if not line or line.startswith('#'):
                    continue
                
                # Parse "natural language -> shell command" format
                if '->' in line:
                    parts = line.split('->', 1)
                    if len(parts) == 2:
                        natural = parts[0].strip()
                        command = parts[1].strip()
                        if natural and command:
                            knowledge.append((natural, command))
        except Exception:
            # If file is corrupted, return empty list
            return []
        
        return knowledge
    
    def search_knowledge(self, query: str, limit: int = 3) -> List[tuple[str, str]]:
        """
        Search knowledge base for relevant entries.
        
        Args:
            query: Natural language query
            limit: Maximum number of results
            
        Returns:
            List of (natural_language, shell_command) tuples
        """
        knowledge = self.load_knowledge()
        query_lower = query.lower()
        
        # Find entries where the natural language contains query words
        matches = []
        for natural, command in knowledge:
            natural_lower = natural.lower()
            
            # Check if query is substring of natural language
            if query_lower in natural_lower:
                matches.append((natural, command))
            # Or check if any word in query matches
            elif any(word in natural_lower for word in query_lower.split()):
                matches.append((natural, command))
        
        return matches[:limit]
    
    def add_entry(self, natural_language: str, shell_command: str):
        """
        Add a new entry to the knowledge base.
        
        Args:
            natural_language: Natural language description
            shell_command: Shell command
        """
        if not natural_language or not shell_command:
            return
        
        # Append to file
        with open(self.knowledge_file, 'a') as f:
            f.write(f"\n{natural_language} -> {shell_command}\n")
    
    def get_knowledge_file_path(self) -> str:
        """Get the path to the knowledge file."""
        return str(self.knowledge_file)
