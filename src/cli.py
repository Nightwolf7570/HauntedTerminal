"""
CLI interface for Haunted Terminal.
Handles user interaction, display, and main REPL loop.
"""

import sqlite3
import time
from datetime import datetime
from typing import List, Optional
from dataclasses import dataclass
from src.theme import ThemeManager
from src.ollama_client import OllamaClient, OllamaConnectionError, OllamaInterpretationError
from src.executor import CommandExecutor, ExecutionResult
from src.safety import classify_command, get_confirmation, CommandRisk
from src.history import HistoryManager
from src.context import ContextManager
from src.rituals import RitualManager
from src.corrector import PathCorrector
from src.knowledge import KnowledgeBase
from src.blacklist import Blacklist
from src.spirits import SpiritSuggestions


@dataclass
class SessionCommand:
    """Represents a command executed in the current session."""
    natural_language: str
    shell_command: str
    result: Optional[ExecutionResult] = None


class HauntedCLI:
    """Main CLI application for Haunted Terminal."""
    
    def __init__(
        self,
        theme: Optional[ThemeManager] = None,
        ollama: Optional[OllamaClient] = None,
        executor: Optional[CommandExecutor] = None,
        history: Optional[HistoryManager] = None
    ):
        """
        Initialize the CLI application.
        
        Args:
            theme: Theme manager for styled output
            ollama: Ollama client for command interpretation
            executor: Command executor for running shell commands
            history: History manager for persistence
        """
        self.theme = theme or ThemeManager()
        self.ollama = ollama or OllamaClient()
        self.executor = executor or CommandExecutor()
        self.history = history or HistoryManager()
        self.context_mgr = ContextManager()
        self.rituals = RitualManager(self.history.db_path)
        self.corrector = PathCorrector()
        self.knowledge = KnowledgeBase()
        self.blacklist = Blacklist()
        self.spirits = SpiritSuggestions(self.history)
        
        self.session_history: List[SessionCommand] = []
        self.last_natural_input: Optional[str] = None
        self.last_failed_command: Optional[str] = None
        self.retry_current_input: bool = False
        self.running = False
    
    def display_welcome(self) -> None:
        """Display clean welcome header."""
        self.theme.display_welcome()
        
        # Display offline operation confirmation
        from src.theme import SUCCESS
        text_obj = self.theme.console.render_str(f"[{SUCCESS}]✓[/{SUCCESS}] offline mode · all processing local")
        self.theme.console.print(text_obj)
        self.theme.console.print()
    
    def handle_builtin_command(self, user_input: str) -> bool:
        """
        Handle built-in commands that don't need Ollama interpretation.
        
        Args:
            user_input: User's input string
            
        Returns:
            True if command was handled, False if it should go to Ollama
        """
        cmd = user_input.lower().strip()
        
        # Help command
        if cmd in ['help', '?', 'commands']:
            self.theme.console.print()
            from src.theme import SECONDARY, STATUS_DIM
            self.theme.console.print(f"[{SECONDARY}]haunted terminal commands[/{SECONDARY}]")
            self.theme.console.print()
            self.theme.console.print(f"[{STATUS_DIM}]  help, ?          show this help message[/{STATUS_DIM}]")
            self.theme.console.print(f"[{STATUS_DIM}]  retry, r         retry last command with different approach[/{STATUS_DIM}]")
            self.theme.console.print(f"[{STATUS_DIM}]  history          show recent command history[/{STATUS_DIM}]")
            self.theme.console.print(f"[{STATUS_DIM}]  ritual           manage and execute workflows[/{STATUS_DIM}]")
            self.theme.console.print(f"[{STATUS_DIM}]  knowledge        edit knowledge base (custom commands)[/{STATUS_DIM}]")
            self.theme.console.print(f"[{STATUS_DIM}]  system           show system status[/{STATUS_DIM}]")
            self.theme.console.print(f"[{STATUS_DIM}]  explain <cmd>    explain a shell command[/{STATUS_DIM}]")
            self.theme.console.print(f"[{STATUS_DIM}]  alias            manage command aliases[/{STATUS_DIM}]")
            self.theme.console.print(f"[{STATUS_DIM}]  clear            clear the screen[/{STATUS_DIM}]")
            self.theme.console.print(f"[{STATUS_DIM}]  exit, quit       exit the application[/{STATUS_DIM}]")
            self.theme.console.print()
            self.theme.console.print(f"[{STATUS_DIM}]or just type what you want to do in plain english[/{STATUS_DIM}]")
            self.theme.console.print()
            return True
        
        # History command
        if cmd == 'history':
            from src.theme import SECONDARY, STATUS_DIM, SUCCESS, DIM
            self.theme.console.print()
            
            # Show session history
            if self.session_history:
                self.theme.console.print(f"[{SECONDARY}]current session[/{SECONDARY}]")
                self.theme.console.print()
                for cmd_obj in self.session_history[-10:]:
                    status = f"[{SUCCESS}]✓[/{SUCCESS}]" if cmd_obj.result and cmd_obj.result.exit_code == 0 else "✗"
                    self.theme.console.print(f"  {status} [{STATUS_DIM}]{cmd_obj.natural_language}[/{STATUS_DIM}]")
                    self.theme.console.print(f"     → {cmd_obj.shell_command}")
                self.theme.console.print()
            
            # Show recent persistent history
            recent = []
            try:
                recent = self.history.get_recent_commands(limit=10)
                if recent:
                    self.theme.console.print(f"[{SECONDARY}]recent history (all sessions)[/{SECONDARY}]")
                    self.theme.console.print()
                    for entry in recent:
                        status = f"[{SUCCESS}]✓[/{SUCCESS}]" if entry.exit_code == 0 else "✗"
                        self.theme.console.print(f"  {status} [{STATUS_DIM}]{entry.natural_language}[/{STATUS_DIM}]")
                        self.theme.console.print(f"     → {entry.shell_command}")
                        timestamp_str = entry.timestamp.strftime("%Y-%m-%d %H:%M:%S")
                        self.theme.console.print(f"     [{DIM}]{timestamp_str}[/{DIM}]")
                    self.theme.console.print()
            except Exception as e:
                self.theme.display_warning(f"could not load persistent history: {str(e)}")
            
            if not self.session_history and not recent:
                self.theme.display_warning("no command history available")
            
            self.theme.console.print()
            return True
        
        # Ritual command
        if cmd == 'ritual':
            from src.theme import SECONDARY, STATUS_DIM, SUCCESS
            self.theme.console.print()
            
            rituals = self.rituals.list_rituals()
            if rituals:
                self.theme.console.print(f"[{SECONDARY}]available rituals[/{SECONDARY}]")
                self.theme.console.print()
                for ritual in rituals:
                    self.theme.console.print(f"  🔮 [{SUCCESS}]{ritual.name}[/{SUCCESS}]")
                    if ritual.description:
                        self.theme.console.print(f"     [{STATUS_DIM}]{ritual.description}[/{STATUS_DIM}]")
                self.theme.console.print()
                self.theme.console.print(f"[{STATUS_DIM}]run with: perform <ritual_name>[/{STATUS_DIM}]")
            else:
                self.theme.console.print(f"[{STATUS_DIM}]no rituals defined yet[/{STATUS_DIM}]")
                self.theme.console.print()
                self.theme.console.print(f"[{STATUS_DIM}]create rituals in ~/.haunted/rituals/[/{STATUS_DIM}]")
            
            self.theme.console.print()
            return True
        
        # Knowledge command
        if cmd == 'knowledge':
            from src.theme import SECONDARY, STATUS_DIM
            self.theme.console.print()
            knowledge_path = self.knowledge.get_knowledge_file_path()
            self.theme.console.print(f"[{SECONDARY}]knowledge base[/{SECONDARY}]")
            self.theme.console.print()
            self.theme.console.print(f"[{STATUS_DIM}]location: {knowledge_path}[/{STATUS_DIM}]")
            self.theme.console.print()
            
            # Show current entries
            entries = self.knowledge.load_knowledge()
            if entries:
                self.theme.console.print(f"[{STATUS_DIM}]current entries:[/{STATUS_DIM}]")
                for natural, command in entries[:10]:
                    self.theme.console.print(f"  • {natural}")
                    self.theme.console.print(f"    → {command}")
                if len(entries) > 10:
                    self.theme.console.print(f"[{STATUS_DIM}]  ... and {len(entries) - 10} more[/{STATUS_DIM}]")
            else:
                self.theme.console.print(f"[{STATUS_DIM}]no entries yet[/{STATUS_DIM}]")
            
            self.theme.console.print()
            self.theme.console.print(f"[{STATUS_DIM}]edit with: open {knowledge_path}[/{STATUS_DIM}]")
            self.theme.console.print()
            return True
        
        # Clear command
        if cmd == 'clear':
            self.theme.console.clear()
            self.display_welcome()
            return True
            
        # Explain command
        if cmd == 'explain':
            cmd_parts = user_input.strip().split(' ', 1)
            if len(cmd_parts) < 2:
                self.theme.display_warning("usage: explain <shell command>")
                return True
            
            target_cmd = cmd_parts[1]
            with self.theme.loading_animation("consulting spirits"):
                explanation = self.ollama.explain_command(target_cmd)
            
            self.theme.console.print()
            from src.theme import ACCENT
            self.theme.console.print(f"[{ACCENT}]Explanation:[/{ACCENT}] {explanation}")
            self.theme.console.print()
            return True

        # Alias commands
        if cmd == 'alias' or cmd == 'aliases':
            cmd_parts = user_input.strip().split(' ', 1)
            
            # List aliases
            if len(cmd_parts) == 1:
                aliases = self.history.list_aliases()
                self.theme.console.print()
                from src.theme import SECONDARY, SUCCESS, ACCENT
                self.theme.console.print(f"[{SECONDARY}]active aliases[/{SECONDARY}]")
                if not aliases:
                    self.theme.console.print("  [dim]no aliases defined[/dim]")
                for name, command in aliases:
                    self.theme.console.print(f"  [{SUCCESS}]{name}[/{SUCCESS}] = [{ACCENT}]{command}[/{ACCENT}]")
                self.theme.console.print()
                return True
            
            # Add alias: alias name = command
            args = cmd_parts[1]
            if '=' in args:
                name, command = [x.strip() for x in args.split('=', 1)]
                self.history.add_alias(name, command)
                self.theme.display_success(f"alias '{name}' created")
            else:
                self.theme.display_warning("usage: alias name = command")
            return True
            
        if cmd == 'unalias':
            cmd_parts = user_input.strip().split(' ', 1)
            if len(cmd_parts) < 2:
                self.theme.display_warning("usage: unalias <name>")
                return True
                
            if self.history.remove_alias(cmd_parts[1]):
                self.theme.display_success(f"alias '{cmd_parts[1]}' removed")
            else:
                self.theme.display_warning(f"alias '{cmd_parts[1]}' not found")
            return True
        
        # System info command
        if cmd == 'system':
            import platform
            import shutil
            import os
            
            self.theme.console.print()
            from src.theme import ACCENT, STATUS_DIM, TEXT
            
            try:
                user = os.getlogin()
            except:
                user = os.environ.get('USER', 'unknown')

            info = {
                "OS": f"{platform.system()} {platform.release()}",
                "Machine": platform.machine(),
                "Python": platform.python_version(),
                "User": user,
                "CWD": self.executor.get_working_directory(),
            }
            
            # Check disk usage for CWD
            try:
                total, used, free = shutil.disk_usage(info["CWD"])
                info["Disk Free"] = f"{free // (2**30)} GB"
            except:
                pass

            self.theme.console.print(f"[{ACCENT}]System Status[/{ACCENT}]")
            for k, v in info.items():
                self.theme.console.print(f"  [{STATUS_DIM}]{k}:[/{STATUS_DIM}] [{TEXT}]{v}[/{TEXT}]")
            self.theme.console.print()
            return True

        # Suggest command
        if cmd.startswith('suggest'):
            parts = user_input.strip().split(' ', 1)
            if len(parts) == 1:
                # No args, suggest for current directory
                cwd = self.executor.get_working_directory()
                suggestions = self.history.get_directory_suggestions(cwd, limit=5)
                title = f"Suggestions for {cwd}"
            else:
                # Query provided
                query = parts[1]
                suggestions = self.history.get_suggestions(query, limit=5)
                title = f"Suggestions matching '{query}'"

            self.theme.console.print()
            if not suggestions:
                self.theme.display_warning("no suggestions found")
            else:
                from src.theme import ACCENT, STATUS_DIM
                self.theme.console.print(f"[{ACCENT}]{title}:[/{ACCENT}]")
                for s in suggestions:
                    self.theme.console.print(f"  [{STATUS_DIM}]{s.natural_language}[/{STATUS_DIM}] → {s.shell_command}")
            self.theme.console.print()
            return True

        # Config command
        if cmd.startswith('config'):
            parts = user_input.strip().split(' ')
            if len(parts) < 3:
                self.theme.display_warning("usage: config <set|get> <key> [value]")
                return True
            
            action = parts[1]
            key = parts[2]
            
            if action == 'set':
                if len(parts) < 4:
                    self.theme.display_warning("value required")
                    return True
                value = " ".join(parts[3:])
                self.history.set_preference(key, value)
                self.theme.display_success(f"preference '{key}' saved")
            elif action == 'get':
                val = self.history.get_preference(key)
                if val:
                    self.theme.display_success(f"{key} = {val}")
                else:
                    self.theme.display_warning(f"preference '{key}' not set")
            return True

        # Ritual command
        if cmd.startswith('ritual'):
            parts = user_input.strip().split(' ', 2)
            if len(parts) < 2:
                self.theme.display_warning("usage: ritual <list|show|run|create|delete> [name]")
                return True
                
            action = parts[1]
            
            if action == 'list':
                rituals = self.rituals.list_rituals()
                self.theme.console.print()
                from src.theme import ACCENT, STATUS_DIM
                self.theme.console.print(f"[{ACCENT}]Saved Rituals:[/{ACCENT}]")
                if not rituals:
                    self.theme.console.print("  [dim]no rituals found[/dim]")
                for r in rituals:
                    self.theme.console.print(f"  [{STATUS_DIM}]{r.name}[/{STATUS_DIM}] - {r.description or 'no description'}")
                self.theme.console.print()
                return True
                
            if len(parts) < 3:
                self.theme.display_warning(f"name required for ritual {action}")
                return True
                
            name = parts[2]
            
            if action == 'show':
                r = self.rituals.get_ritual(name)
                if r:
                    self.theme.console.print()
                    from src.theme import ACCENT
                    self.theme.console.print(f"[{ACCENT}]Ritual: {r.name}[/{ACCENT}]")
                    self.theme.console.print(f"[dim]{r.description}[/dim]")
                    for step in r.steps:
                        self.theme.console.print(f"  {step.order + 1}. {step.command}")
                    self.theme.console.print()
                else:
                    self.theme.display_warning(f"ritual '{name}' not found")
                return True
                
            if action == 'delete':
                if self.rituals.delete_ritual(name):
                    self.theme.display_success(f"ritual '{name}' deleted")
                else:
                    self.theme.display_warning(f"ritual '{name}' not found")
                return True
                
            if action == 'run':
                r = self.rituals.get_ritual(name)
                if not r:
                    self.theme.display_warning(f"ritual '{name}' not found")
                    return True
                
                self.theme.console.print()
                self.theme.display_success(f"starting ritual: {name}")
                
                for step in r.steps:
                    self.theme.console.print(f"Step {step.order + 1}: {step.command}")
                    # Execute without confirmation for now, or maybe ask once?
                    # For safety, let's re-use existing execution flow or direct executor
                    # Direct executor is safer for automation, but less interactive
                    try:
                        res = self.executor.execute(step.command)
                        self.display_output(res)
                        if res.exit_code != 0:
                            if self.theme.prompt_confirmation("step failed. continue?") != 'y':
                                break
                    except Exception as e:
                        self.theme.display_error(f"failed to execute step: {e}")
                        break
                return True
                
            if action == 'create':
                self.theme.console.print()
                self.theme.display_success(f"Creating ritual '{name}'")
                self.theme.console.print()
                
                # Get description
                from src.theme import STATUS_DIM
                self.theme.console.print(f"[{STATUS_DIM}]Description (optional):[/{STATUS_DIM}] ", end="")
                desc = input().strip()
                
                # Get commands
                self.theme.console.print(f"[{STATUS_DIM}]Enter commands one by one. Type 'done' to finish.[/{STATUS_DIM}]")
                self.theme.console.print()
                
                steps = []
                while True:
                    self.theme.console.print(f"[{STATUS_DIM}]step {len(steps) + 1} >[/{STATUS_DIM}] ", end="")
                    cmd = input().strip()
                    if cmd.lower() == 'done':
                        break
                    if cmd:
                        steps.append(cmd)
                        self.theme.console.print(f"  [{STATUS_DIM}]✓ added[/{STATUS_DIM}]")
                
                self.theme.console.print()
                
                if steps:
                    self.rituals.create_ritual(name, desc, steps)
                    self.theme.display_success(f"ritual '{name}' saved with {len(steps)} steps")
                else:
                    self.theme.display_warning("ritual cancelled (no steps)")
                
                self.theme.console.print()
                return True
                
            return True

        return False
    
    def get_user_input(self) -> Optional[str]:
        """
        Get natural language input from user with validation.
        
        Returns:
            User input string, or None if user wants to exit
        """
        try:
            user_input = self.theme.get_input()
            
            # Handle exit commands
            if user_input.lower() in ['exit', 'quit']:
                return None
            
            # Validate input length (Requirements 1.2, 1.3)
            if not user_input or not user_input.strip():
                self.theme.display_warning("empty input")
                return ""
            
            if len(user_input) > 1000:
                self.theme.display_error(
                    "input too long (max 1000 characters)",
                    "try breaking it into smaller commands"
                )
                return ""
            
            return user_input.strip()
            
        except (KeyboardInterrupt, EOFError):
            # Handle Ctrl+C or Ctrl+D gracefully
            return None
    
    def display_command_preview(self, original_input: str, shell_command: str) -> None:
        """
        Display command preview with clean formatting.
        
        Args:
            original_input: Original natural language input
            shell_command: Interpreted shell command
        """
        self.theme.command_preview(original_input, shell_command)
    
    def display_output(self, result: ExecutionResult) -> None:
        """
        Display command execution results with themed formatting.
        
        Args:
            result: Execution result containing stdout, stderr, exit code
        """
        # Use the theme manager's display_result method for consistent themed output
        self.theme.display_result(
            stdout=result.stdout,
            stderr=result.stderr,
            exit_code=result.exit_code,
            execution_time=result.execution_time
        )
    
    def run(self) -> int:
        """
        Start the main REPL loop.
        
        Returns:
            Exit code (0 for success)
        """
        # Display welcome banner
        self.display_welcome()
        
        # Check Ollama connection (Requirement 7.2)
        try:
            self.ollama.check_connection()
            self.theme.display_success("connected to ollama")
        except OllamaConnectionError as e:
            # Requirement 7.2: Provide specific troubleshooting steps
            self.theme.display_error(
                "cannot connect to ollama",
                "1. Install from https://ollama.ai\n"
                "  2. Run 'ollama serve'\n"
                "  3. Pull model: 'ollama pull llama3.2'"
            )
            self.theme.console.print()
            self.theme.display_warning("command interpretation unavailable")
        except Exception as e:
            # Requirement 7.1, 7.4: Catch unexpected errors during startup
            self.theme.display_error(
                "unexpected error during connection check",
                str(e)
            )
            self.theme.console.print()
        
        self.theme.console.print()
        self.running = True
        
        # Main REPL loop
        while self.running:
            try:
                # Get user input (with validation error handling)
                # Unless we're retrying the current input
                if not self.retry_current_input:
                    try:
                        user_input = self.get_user_input()
                    except (KeyboardInterrupt, EOFError):
                        # Handle Ctrl+C or Ctrl+D gracefully
                        self._display_farewell()
                        break
                    except Exception as e:
                        # Requirement 7.1, 7.5: Handle input errors gracefully
                        self.theme.display_error(
                            "Error reading input",
                            f"Details: {str(e)}"
                        )
                        self.theme.console.print()
                        continue
                    
                    # Handle exit
                    if user_input is None:
                        self._display_farewell()
                        break
                    
                    # Skip empty input (validation error already displayed)
                    if not user_input:
                        continue
                else:
                    # We're retrying - use the last natural input
                    user_input = self.last_natural_input
                    self.retry_current_input = False  # Reset flag
                
                # Check for alias expansion
                alias_expansion = self.history.get_alias(user_input)
                if alias_expansion:
                    from src.theme import STATUS_DIM
                    self.theme.console.print(f"[{STATUS_DIM}]expanded alias: {user_input} → {alias_expansion}[/{STATUS_DIM}]")
                    user_input = alias_expansion
                
                # Check if this is a retry command
                is_retry = user_input.lower().strip() in ['retry', 'r', 'again']
                
                # Show spirit suggestion if available
                if not is_retry and len(user_input) >= 3:
                    suggestion = self.spirits.get_suggestion(
                        user_input,
                        self.executor.get_working_directory(),
                        datetime.now()
                    )
                    if suggestion:
                        from src.theme import STATUS_DIM, SECONDARY
                        suggestion_text, reason = suggestion
                        self.theme.console.print()
                        self.theme.console.print(
                            f"[{STATUS_DIM}]the spirits whisper: [{SECONDARY}]\"{suggestion_text}\"[/{SECONDARY}] ({reason})[/{STATUS_DIM}]"
                        )
                        self.theme.console.print()
                
                # Check if this is a ritual execution command
                if user_input.lower().startswith('perform '):
                    ritual_name = user_input[8:].strip()
                    self._execute_ritual(ritual_name)
                    continue
                
                # Handle built-in commands first (but retry needs special handling)
                if not is_retry and self.handle_builtin_command(user_input):
                    continue
                
                # If retry, use the last natural input
                if is_retry:
                    if not self.last_natural_input:
                        self.theme.display_warning("no previous command to retry")
                        self.theme.console.print()
                        continue
                    
                    from src.theme import SECONDARY, STATUS_DIM
                    self.theme.console.print()
                    self.theme.console.print(f"[{SECONDARY}]retrying:[/{SECONDARY}] [{STATUS_DIM}]{self.last_natural_input}[/{STATUS_DIM}]")
                    self.theme.console.print()
                    user_input = self.last_natural_input
                else:
                    # Store this as the last natural input for potential retry
                    self.last_natural_input = user_input
                
                # Get context
                context_str = self.context_mgr.get_context_string()

                # Get learned history and rejections
                learned_history = [
                    (h.natural_language, h.shell_command) 
                    for h in self.history.get_suggestions(user_input, limit=3)
                ]
                rejections = self.history.get_rejections(user_input, limit=3)
                
                # Get knowledge base entries
                knowledge_entries = self.knowledge.search_knowledge(user_input, limit=3)
                
                # Combine learned history with knowledge base (knowledge base takes priority)
                combined_history = knowledge_entries + learned_history
                
                # Get blacklist patterns
                blacklist_patterns = self.blacklist.load_blacklist()
                
                # If retrying, add the last failed command to rejections
                if is_retry and self.last_failed_command:
                    rejections = [self.last_failed_command] + rejections

                # Interpret command with Ollama
                try:
                    try:
                        with self.theme.loading_animation("thinking"):
                            shell_command = self.ollama.interpret_command(
                                user_input, 
                                context=context_str,
                                history=combined_history,
                                rejections=rejections,
                                blacklist=blacklist_patterns
                            )
                    except KeyboardInterrupt:
                        # User pressed Ctrl+C during processing
                        self.theme.console.print()
                        self.theme.display_warning("cancelled · press ctrl+c again or type 'exit' to quit")
                        self.theme.console.print()
                        continue
                    
                    # Auto-correct paths
                    cwd = self.executor.get_working_directory()
                    original_cmd = shell_command
                    shell_command = self.corrector.correct_paths(shell_command, cwd)
                    
                    if shell_command != original_cmd:
                        from src.theme import STATUS_DIM
                        self.theme.console.print()
                        self.theme.console.print(f"[{STATUS_DIM}]path corrected: {original_cmd} → {shell_command}[/{STATUS_DIM}]")
                    
                    self.theme.console.print()
                    
                except OllamaConnectionError as e:
                    # Requirement 7.2: Specific troubleshooting for connection failures
                    self.theme.display_error(
                        "cannot reach ollama",
                        "check if ollama is running: 'ollama serve'"
                    )
                    self.theme.console.print()
                    continue
                
                except OllamaInterpretationError as e:
                    # Requirement 7.1: Command interpretation error handling
                    self.theme.display_error(
                        "could not interpret command",
                        "try rephrasing or being more specific"
                    )
                    self.theme.console.print()
                    continue
                
                except Exception as e:
                    # Requirement 7.1, 7.4: Catch unexpected Ollama errors
                    self.theme.display_error(
                        "unexpected interpretation error",
                        str(e)
                    )
                    self.theme.console.print()
                    continue
                
                # Validate command syntax
                try:
                    if not self.executor.validate_syntax(shell_command):
                        # Requirement 7.1: Validation error handling
                        self.theme.display_error(
                            "invalid command syntax",
                            f"command: {shell_command}"
                        )
                        self.theme.console.print()
                        continue
                except Exception as e:
                    # Requirement 7.1, 7.4: Handle validation errors
                    self.theme.display_error(
                        "validation error",
                        str(e)
                    )
                    self.theme.console.print()
                    continue
                
                # Display command preview
                self.display_command_preview(user_input, shell_command)
                
                # Check command safety and get confirmation
                try:
                    risk = classify_command(shell_command)
                    confirmation = get_confirmation(shell_command, risk, self.theme.console)
                except Exception as e:
                    # Requirement 7.1, 7.4: Handle safety check errors
                    self.theme.display_error(
                        "Error during safety check",
                        f"Details: {str(e)}\n"
                        "  • Command will not be executed for safety"
                    )
                    self.theme.console.print()
                    continue
                
                # Handle retry from confirmation
                if confirmation == "retry":
                    self.theme.console.print()
                    from src.theme import SECONDARY, STATUS_DIM
                    self.theme.console.print(f"[{SECONDARY}]retrying:[/{SECONDARY}] [{STATUS_DIM}]{user_input}[/{STATUS_DIM}]")
                    self.theme.console.print()
                    
                    # Add this command to rejections and retry
                    self.last_failed_command = shell_command
                    
                    # Set flag to retry with same input
                    self.retry_current_input = True
                    
                    # Go back to start of loop to reinterpret
                    continue
                
                if confirmation == "no":
                    self.theme.display_warning("command cancelled")
                    
                    # Log cancelled command (especially for destructive ones)
                    if risk == CommandRisk.DESTRUCTIVE:
                        session_cmd = SessionCommand(
                            natural_language=user_input,
                            shell_command=shell_command,
                            result=None
                        )
                        self.session_history.append(session_cmd)
                    
                    self.theme.console.print()
                    continue
                
                # Execute command
                self.theme.console.print()
                
                try:
                    result = self.executor.execute(shell_command)
                except ValueError as e:
                    # Requirement 7.1: Command execution validation errors
                    self.theme.display_error(
                        "Command execution failed validation",
                        f"Details: {str(e)}"
                    )
                    self.theme.console.print()
                    continue
                except Exception as e:
                    # Requirement 7.1, 7.3, 7.4: Unexpected execution errors
                    self.theme.display_error(
                        "Unexpected error during command execution",
                        f"Details: {str(e)}\n"
                        "  • The command could not be executed\n"
                        "  • Check if the command is valid for your system"
                    )
                    self.theme.console.print()
                    continue
                
                # Display output (Requirement 7.3: Display stderr with helpful context)
                self.display_output(result)
                
                # Save to session history
                session_cmd = SessionCommand(
                    natural_language=user_input,
                    shell_command=shell_command,
                    result=result
                )
                self.session_history.append(session_cmd)
                
                # Save successful commands to persistent history
                if result.exit_code == 0:
                    # Clear last failed command on success
                    self.last_failed_command = None
                    
                    # Clear any rejections for this input since we found a working command
                    try:
                        self.history.clear_rejections(user_input)
                    except Exception:
                        pass  # Fail silently
                    
                    try:
                        self.history.save_command(
                            natural_language=user_input,
                            shell_command=shell_command,
                            exit_code=result.exit_code,
                            execution_time=result.execution_time,
                            working_directory=self.executor.get_working_directory()
                        )
                    except sqlite3.Error as e:
                        # Requirement 7.4: Database error graceful degradation
                        self.theme.display_warning(
                            f"Could not save to history database: {str(e)}\n"
                            "  • History features may be unavailable\n"
                            "  • The application will continue normally"
                        )
                        self.theme.console.print()
                    except Exception as e:
                        # Requirement 7.4: Other history save errors
                        self.theme.display_warning(
                            f"Unexpected error saving to history: {str(e)}\n"
                            "  • History features may be unavailable"
                        )
                        self.theme.console.print()
                else:
                    # Track failed command for retry
                    self.last_failed_command = shell_command
                    
                    # Only add to rejections if command actually failed (not just cancelled)
                    # This helps Ollama learn from actual failures, not user preferences
                    try:
                        self.history.add_rejection(user_input, shell_command)
                    except Exception:
                        pass  # Fail silently on logging
                    
                    # Show retry hint
                    from src.theme import STATUS_DIM
                    self.theme.console.print(f"[{STATUS_DIM}]tip: type 'retry' or 'r' to try a different approach[/{STATUS_DIM}]")
                    self.theme.console.print()
                
            except KeyboardInterrupt:
                # Requirement 7.5: Handle Ctrl+C gracefully
                self.theme.console.print()
                self.theme.display_warning("interrupted · press ctrl+c again or type 'exit' to quit")
                self.theme.console.print()
                continue
            
            except Exception as e:
                # Requirement 7.1, 7.4, 7.5: Catch all other exceptions
                import traceback
                error_details = traceback.format_exc()
                
                self.theme.display_error(
                    "An unexpected error occurred in the main loop",
                    f"Details: {str(e)}\n"
                    "  • The application will continue running\n"
                    "  • If this persists, please report the issue"
                )
                
                # Log full traceback for debugging (could be written to file in production)
                self.theme.console.print()
                # Escape brackets in error details to prevent Rich markup errors
                safe_error_details = error_details.replace("[", "\\[").replace("]", "\\]")
                self.theme.console.print(f"[dim]Stack trace: {safe_error_details}[/dim]")
                self.theme.console.print()
                
                # Requirement 7.5: Continue running - don't crash
                continue
        
        return 0
    
    def _execute_ritual(self, ritual_name: str) -> None:
        """Execute a ritual workflow with visual feedback."""
        from src.rituals import StepStatus
        
        # Load the ritual
        ritual = self.rituals.get_ritual(ritual_name)
        if not ritual:
            self.theme.display_error(f"ritual not found: {ritual_name}")
            self.theme.console.print()
            return
        
        # Display start banner
        self.theme.display_ritual_start(ritual.name, len(ritual.steps))
        
        # Define executor function
        def execute_command(cmd: str) -> tuple[int, str, str]:
            result = self.executor.execute(cmd)
            return (result.exit_code, result.stdout, result.stderr)
        
        # Define progress callback
        def progress_callback(step, step_num, total):
            self.theme.display_ritual_step(step_num, total, step.command, "running")
        
        # Execute the ritual
        start_time = time.time()
        execution = self.rituals.execute_ritual(ritual, execute_command, progress_callback)
        total_time = time.time() - start_time
        
        # Display results for each step
        self.theme.console.print()
        for i, step in enumerate(ritual.steps):
            status_str = "success" if step.status == StepStatus.SUCCESS else "failed"
            self.theme.display_ritual_step(i + 1, len(ritual.steps), step.command, status_str)
            
            if step.output and step.output.strip():
                # Escape brackets in output to prevent Rich markup errors
                safe_output = step.output.strip().replace("[", "\\[").replace("]", "\\]")
                self.theme.console.print(f"  [dim]{safe_output}[/dim]")
                self.theme.console.print()
            
            if step.status == StepStatus.FAILED and step.error:
                self.theme.display_error(f"step {i + 1} failed", step.error)
                self.theme.console.print()
                break
        
        # Display completion banner
        self.theme.display_ritual_complete(execution.success, total_time)
    
    def _display_farewell(self) -> None:
        """Display clean farewell message."""
        self.theme.console.print()
        
        from src.theme import Text, STATUS_DIM
        farewell = Text()
        farewell.append("goodbye", style=STATUS_DIM)
        self.theme.console.print(farewell)
        
        # Show session summary
        if self.session_history:
            executed_count = sum(1 for cmd in self.session_history if cmd.result is not None)
            summary = Text()
            summary.append(f"{executed_count} commands executed this session", style=STATUS_DIM)
            self.theme.console.print(summary)
        
        self.theme.console.print()
    
    def get_session_history(self) -> List[SessionCommand]:
        """
        Get the command history for the current session.
        
        Returns:
            List of SessionCommand objects
        """
        return self.session_history.copy()


def main() -> int:
    """
    Main entry point for the CLI application.
    
    Returns:
        Exit code (0 for success)
    """
    cli = HauntedCLI()
    return cli.run()


if __name__ == "__main__":
    import sys
    sys.exit(main())
