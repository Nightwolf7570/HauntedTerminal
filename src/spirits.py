"""
The Spirits Know - Predictive command suggestions.
Suggests commands based on history, context, and patterns.
"""

from datetime import datetime
from typing import List, Optional, Tuple
from src.history import HistoryManager


class SpiritSuggestions:
    """Provides predictive command suggestions."""
    
    def __init__(self, history: HistoryManager):
        self.history = history
    
    def get_suggestion(
        self, 
        partial_input: str, 
        current_directory: str,
        time_of_day: Optional[datetime] = None
    ) -> Optional[Tuple[str, str]]:
        """
        Get a suggestion based on partial input and context.
        
        Args:
            partial_input: What the user has typed so far
            current_directory: Current working directory
            time_of_day: Current time (for time-based patterns)
            
        Returns:
            Tuple of (natural_language_suggestion, confidence_reason) or None
        """
        if not partial_input or len(partial_input) < 3:
            return None
        
        partial_lower = partial_input.lower().strip()
        
        # Try to find matching commands from history
        suggestions = self._get_history_suggestions(partial_lower)
        
        if suggestions:
            # Return the most frequent/recent match
            return suggestions[0]
        
        # Try pattern-based suggestions
        pattern_suggestion = self._get_pattern_suggestion(partial_lower, time_of_day)
        if pattern_suggestion:
            return pattern_suggestion
        
        return None
    
    def _get_history_suggestions(self, partial: str) -> List[Tuple[str, str]]:
        """Get suggestions from command history."""
        try:
            # Search for commands that start with or contain the partial input
            recent = self.history.get_recent_commands(limit=50)
            
            matches = []
            for entry in recent:
                nl_lower = entry.natural_language.lower()
                
                # Exact prefix match (highest priority)
                if nl_lower.startswith(partial):
                    matches.append((
                        entry.natural_language,
                        "you've done this before"
                    ))
                # Contains match (lower priority)
                elif partial in nl_lower:
                    matches.append((
                        entry.natural_language,
                        "similar to past commands"
                    ))
            
            # Remove duplicates while preserving order
            seen = set()
            unique_matches = []
            for match in matches:
                if match[0] not in seen:
                    seen.add(match[0])
                    unique_matches.append(match)
            
            return unique_matches[:3]
        except Exception:
            return []
    
    def _get_pattern_suggestion(
        self, 
        partial: str, 
        time_of_day: Optional[datetime]
    ) -> Optional[Tuple[str, str]]:
        """Get suggestions based on common patterns."""
        
        # Common command patterns
        patterns = {
            'find': ('find python files', 'common search'),
            'list': ('list all files', 'common operation'),
            'show': ('show disk usage', 'common info request'),
            'git': self._get_git_suggestion(partial, time_of_day),
            'open': ('open current directory', 'common action'),
            'search': ('search for files', 'common operation'),
            'create': ('create new directory', 'common task'),
            'delete': ('delete file', 'common operation'),
            'copy': ('copy file', 'common operation'),
            'move': ('move file', 'common operation'),
        }
        
        for keyword, suggestion in patterns.items():
            if partial.startswith(keyword):
                if suggestion:
                    return suggestion
        
        return None
    
    def _get_git_suggestion(
        self, 
        partial: str, 
        time_of_day: Optional[datetime]
    ) -> Optional[Tuple[str, str]]:
        """Get git-specific suggestions based on time and context."""
        
        # Morning = likely starting work (pull)
        # Evening = likely finishing work (push)
        if time_of_day:
            hour = time_of_day.hour
            if 6 <= hour < 12:
                return ('git pull latest changes', 'morning routine')
            elif 17 <= hour < 23:
                return ('git push my changes', 'evening routine')
        
        # Default git suggestions
        if 'git st' in partial or 'git s' in partial:
            return ('git status', 'common git command')
        elif 'git co' in partial:
            return ('git commit changes', 'common git command')
        elif 'git pu' in partial:
            if 'push' in partial:
                return ('git push to remote', 'common git command')
            else:
                return ('git pull from remote', 'common git command')
        
        return ('git status', 'common starting point')
    
    def format_suggestion(self, suggestion: str, reason: str) -> str:
        """Format a suggestion for display."""
        return f"the spirits whisper: \"{suggestion}\" ({reason})"
