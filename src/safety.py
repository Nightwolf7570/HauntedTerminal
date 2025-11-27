"""
Safety manager for detecting and handling destructive commands.
"""
import re
from enum import Enum
from typing import Tuple
from rich.console import Console
from rich.prompt import Prompt
from rich.text import Text


class CommandRisk(Enum):
    """Risk levels for commands."""
    SAFE = "safe"
    MODERATE = "moderate"
    DESTRUCTIVE = "destructive"


# Patterns that indicate destructive operations
DESTRUCTIVE_PATTERNS = [
    # File deletion and modification - per Requirement 4.5
    r'\brm\b',                # any rm command
    r'\bmv\b',                # move/rename can delete/overwrite files
    
    # Disk operations
    r'\bdd\b',                # dd command
    r'\bmkfs\b',              # make filesystem
    r'\bformat\b',            # format command
    
    # System modifications
    r'\bchmod\s+-r',          # recursive permission changes (lowercase because we convert to lower)
    r'\bchown\s+-r',          # recursive ownership changes (lowercase because we convert to lower)
    
    # Package management (potentially destructive)
    r'\bapt\s+remove',
    r'\bapt\s+purge',
    r'\byum\s+remove',
    r'\bpip\s+uninstall',
    
    # Truncation (but not 2>/dev/null which is safe)
    r'(?<!2)>\s*/dev/(?!null)',  # redirecting to device files (except 2>/dev/null)
    r'\btruncate\b',
]

# Patterns that indicate moderate risk
MODERATE_PATTERNS = [
    r'\bcp\s+.*\s+-f',        # forced copy
    r'\bchmod\b',             # permission changes (not recursive)
    r'\bchown\b',             # ownership changes (not recursive)
    r'\bkill\b',              # killing processes
    r'\bpkill\b',
    r'\bkillall\b',
]


def classify_command(command: str) -> CommandRisk:
    """
    Classify a command based on its risk level.
    
    Args:
        command: The shell command to classify
        
    Returns:
        CommandRisk enum indicating the risk level
        
    Raises:
        ValueError: If command is None (empty strings are treated as SAFE)
    """
    if command is None:
        raise ValueError("Command cannot be None")
    
    if not command or not command.strip():
        return CommandRisk.SAFE
    
    try:
        command_lower = command.lower()
        
        # Check for destructive patterns
        for pattern in DESTRUCTIVE_PATTERNS:
            try:
                if re.search(pattern, command_lower):
                    return CommandRisk.DESTRUCTIVE
            except re.error as e:
                # If a pattern is malformed, log and continue
                # This shouldn't happen with our hardcoded patterns, but be defensive
                continue
        
        # Check for moderate risk patterns
        for pattern in MODERATE_PATTERNS:
            try:
                if re.search(pattern, command_lower):
                    return CommandRisk.MODERATE
            except re.error as e:
                # If a pattern is malformed, log and continue
                continue
        
        return CommandRisk.SAFE
        
    except Exception as e:
        # If anything unexpected happens, treat as safe to avoid blocking commands
        # In production, this should be logged
        return CommandRisk.SAFE


def get_confirmation(command: str, risk: CommandRisk, console: Console = None) -> str:
    """
    Get user confirmation for command execution based on risk level.
    
    Args:
        command: The shell command to confirm
        risk: The risk level of the command
        console: Rich console for themed output (optional)
        
    Returns:
        "yes" if user confirms, "no" if cancelled, "retry" if user wants to retry
        
    Raises:
        ValueError: If command or risk is invalid
    """
    if command is None:
        raise ValueError("Command cannot be None")
    if not isinstance(risk, CommandRisk):
        raise ValueError(f"Invalid risk type: {type(risk)}")
    
    if console is None:
        console = Console()
    
    try:
        if risk == CommandRisk.SAFE:
            # Simple yes/no/retry for safe commands
            try:
                response = Prompt.ask(
                    "Execute this command?",
                    choices=["y", "n", "r", "yes", "no", "retry"],
                    default="y"
                )
                response_lower = response.lower()
                if response_lower in ["y", "yes"]:
                    return "yes"
                elif response_lower in ["r", "retry"]:
                    return "retry"
                else:
                    return "no"
            except (KeyboardInterrupt, EOFError):
                # User cancelled with Ctrl+C or Ctrl+D
                return "no"
        
        elif risk == CommandRisk.MODERATE:
            # Warning with yes/no/retry
            try:
                warning = Text()
                warning.append("⚡ ", style="bold orange1")
                warning.append("CAUTION: ", style="bold orange1")
                warning.append("This command may modify your system\n", style="orange1")
                console.print(warning)
                
                response = Prompt.ask(
                    "Proceed with execution?",
                    choices=["y", "n", "r", "yes", "no", "retry"],
                    default="n"
                )
                response_lower = response.lower()
                if response_lower in ["y", "yes"]:
                    return "yes"
                elif response_lower in ["r", "retry"]:
                    return "retry"
                else:
                    return "no"
            except (KeyboardInterrupt, EOFError):
                # User cancelled with Ctrl+C or Ctrl+D
                return "no"
        
        else:  # DESTRUCTIVE
            # Prominent warning with explicit typed confirmation
            try:
                console.print()
                
                # Full width border
                border_width = 80
                console.print("═" * border_width, style="bold red")
                
                # Center the warning message
                warning = Text()
                warning.append("💀 DANGER: DESTRUCTIVE OPERATION DETECTED 💀", style="bold red")
                console.print(warning, justify="center")
                
                # Full width border
                console.print("═" * border_width, style="bold red")
                console.print()
                
                console.print(f"Command: {command}", style="bold white")
                console.print()
                console.print(
                    "⚠  This command may permanently delete files or damage your system",
                    style="red"
                )
                console.print()
                
                # Require explicit typed confirmation
                confirmation_text = "EXECUTE"
                response = Prompt.ask(
                    f"Type '{confirmation_text}' to proceed, 'retry' to try different command, or anything else to cancel"
                )
                
                if response == confirmation_text:
                    return "yes"
                elif response.lower() in ["retry", "r"]:
                    return "retry"
                else:
                    return "no"
            except (KeyboardInterrupt, EOFError):
                # User cancelled with Ctrl+C or Ctrl+D
                return "no"
    
    except Exception as e:
        # If anything unexpected happens during confirmation, default to not executing
        # This is the safe choice - better to not execute than to execute without proper confirmation
        console.print(f"\n[red]Error during confirmation: {str(e)}[/red]")
        console.print("[yellow]Defaulting to cancel for safety[/yellow]")
        return "no"
