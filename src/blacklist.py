"""
Blacklist manager for patterns Ollama should never use.
"""

from pathlib import Path
from typing import List


class Blacklist:
    """Manages patterns that should never appear in generated commands."""
    
    def __init__(self, blacklist_file: str = None):
        """
        Initialize blacklist.
        
        Args:
            blacklist_file: Path to blacklist file. Defaults to ~/.haunted/blacklist.txt
        """
        if blacklist_file is None:
            home = Path.home()
            haunted_dir = home / ".haunted"
            haunted_dir.mkdir(exist_ok=True)
            self.blacklist_file = haunted_dir / "blacklist.txt"
        else:
            self.blacklist_file = Path(blacklist_file)
        
        # Create default blacklist if it doesn't exist
        if not self.blacklist_file.exists():
            self._create_default_blacklist()
    
    def _create_default_blacklist(self):
        """Create a default blacklist file."""
        default_content = """# Haunted Terminal Blacklist
# Patterns that should NEVER appear in generated commands
# One pattern per line, case-insensitive

# Example: Prevent specific files
# LinkedListInsertAfter.java

# Example: Prevent dangerous patterns
# rm -rf /

# Add your blacklisted patterns below:
"""
        self.blacklist_file.write_text(default_content)
    
    def load_blacklist(self) -> List[str]:
        """
        Load blacklist patterns from file.
        
        Returns:
            List of blacklisted patterns
        """
        if not self.blacklist_file.exists():
            return []
        
        patterns = []
        try:
            content = self.blacklist_file.read_text()
            for line in content.split('\n'):
                line = line.strip()
                
                # Skip comments and empty lines
                if not line or line.startswith('#'):
                    continue
                
                patterns.append(line)
        except Exception:
            return []
        
        return patterns
    
    def add_pattern(self, pattern: str):
        """
        Add a pattern to the blacklist.
        
        Args:
            pattern: Pattern to blacklist
        """
        if not pattern or not pattern.strip():
            return
        
        # Append to file
        with open(self.blacklist_file, 'a') as f:
            f.write(f"{pattern.strip()}\n")
    
    def get_blacklist_file_path(self) -> str:
        """Get the path to the blacklist file."""
        return str(self.blacklist_file)
