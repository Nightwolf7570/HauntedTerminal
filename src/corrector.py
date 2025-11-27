"""
Path correction utility for fuzzy matching file paths in commands.
"""

import os
import shlex
import difflib
from typing import List, Optional

class PathCorrector:
    """
    Corrects file paths in shell commands using fuzzy matching against the current directory.
    """
    
    def __init__(self, cutoff: float = 0.6):
        """
        Initialize the corrector.
        
        Args:
            cutoff: Similarity threshold for fuzzy matching (0.0 to 1.0).
        """
        self.cutoff = cutoff

    def correct_paths(self, command: str, working_directory: str) -> str:
        """
        Analyze a shell command and attempt to correct non-existent paths 
        by fuzzy matching against files in the working directory.
        
        Args:
            command: The shell command to correct.
            working_directory: The directory to search for files.
            
        Returns:
            The corrected command (or original if no corrections found).
        """
        try:
            # basic safety check for complex commands
            if '|' in command or '>' in command or '&&' in command:
                # Parsing complex pipelines is risky; skip correction
                return command
                
            parts = shlex.split(command)
        except ValueError:
            # shlex failed (e.g. unbalanced quotes), return original
            return command
            
        if not parts:
            return command
            
        # Get list of actual files
        try:
            actual_files = os.listdir(working_directory)
        except OSError:
            return command
            
        corrected_parts = []
        modified = False
        
        # Skip the first part (the command itself) usually
        # But for simplicity we iterate all, though correcting the command name itself 
        # (like 'pyhton' -> 'python') is a different scope. 
        # Let's focus on arguments (indices 1+).
        
        corrected_parts.append(parts[0])
        
        for part in parts[1:]:
            # If it's a flag, skip
            if part.startswith('-'):
                corrected_parts.append(part)
                continue
                
            # Check if path exists as-is
            full_path = os.path.join(working_directory, part)
            if os.path.exists(full_path):
                # It exists, but on case-insensitive filesystems (macOS/Windows),
                # the casing might still be "wrong" compared to the actual file.
                if part in actual_files:
                    corrected_parts.append(part)
                elif os.sep not in part and '/' not in part:
                    # Exists but not exact match in root, and no separators -> likely case mismatch
                    case_match = self._find_case_insensitive(part, actual_files)
                    if case_match:
                        corrected_parts.append(case_match)
                        modified = True
                    else:
                        corrected_parts.append(part)
                else:
                    # Path with separators, or not found in listdir (hidden?), keep as is
                    corrected_parts.append(part)
                continue
                
            # Not found, try fuzzy match
            matches = difflib.get_close_matches(part, actual_files, n=1, cutoff=self.cutoff)
            
            if matches:
                # We found a close match!
                # But wait, is it a better match than just a case-insensitive check?
                # Prioritize case-insensitive exact match
                case_match = self._find_case_insensitive(part, actual_files)
                if case_match:
                    corrected_parts.append(case_match)
                else:
                    corrected_parts.append(matches[0])
                modified = True
            else:
                # Try case-insensitive as a fallback even if fuzzy failed high cutoff
                case_match = self._find_case_insensitive(part, actual_files)
                if case_match:
                    corrected_parts.append(case_match)
                    modified = True
                else:
                    corrected_parts.append(part)
        
        if modified:
            return shlex.join(corrected_parts)
        
        return command

    def _find_case_insensitive(self, target: str, options: List[str]) -> Optional[str]:
        """Find an exact case-insensitive match."""
        target_lower = target.lower()
        for opt in options:
            if opt.lower() == target_lower:
                return opt
        return None
