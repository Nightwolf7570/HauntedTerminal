"""
Theme manager for Haunted Terminal CLI.
Clean, minimal, modern design inspired by Gemini CLI.
"""

import time
import threading
import random
from rich.console import Console
from rich.text import Text
from rich.live import Live
from rich.spinner import Spinner

# Color Palette - Standard ANSI Colors for better compatibility
BACKGROUND = "default"  # Let terminal handle background
ACCENT = "cyan"         # Standard bright cyan
SECONDARY = "magenta"   # Standard purple/magenta
TEXT = "white"          # Standard white
DIM = "dim white"       # Dimmed white
STATUS_DIM = "green"    # Standard green for status
SUCCESS = "green"       # Standard green
ERROR = "red"           # Standard red
WARNING = "yellow"      # Standard yellow

# Prompt symbols
PROMPT_SYMBOL = "›"  # Clean, simple prompt
SYSTEM_PREFIX = "oracle:"
VERSION = "0.1.0"

# Spooky phrases for loading animation
SPOOKY_PHRASES = [
    "consulting the spirits...",
    "communing with the void...",
    "decrypting spectral signals...",
    "opening the portal...",
    "summoning daemons...",
    "reading the bones...",
    "gazing into the abyss...",
    "translating ectoplasm...",
    "whispering to shadows...",
    "channeling dark energy...",
    "manifesting command...",
    "asking the oracle...",
]


class ThemeManager:
    """Manages all themed output for the Haunted Terminal."""
    
    def __init__(self, quiet_mode: bool = False):
        self.console = Console()
        self.quiet_mode = quiet_mode
        self.model_name = "llama3.2"
    
    def generate_gradient(self, start_hex: str, end_hex: str, steps: int) -> list[str]:
        """Generate a smooth gradient of hex codes between two colors."""
        # Parse hex to RGB
        def hex_to_rgb(h):
            h = h.lstrip('#')
            return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

        # Format RGB back to hex
        def rgb_to_hex(rgb):
            return '#{:02x}{:02x}{:02x}'.format(int(rgb[0]), int(rgb[1]), int(rgb[2]))

        start_rgb = hex_to_rgb(start_hex)
        end_rgb = hex_to_rgb(end_hex)
        
        gradient = []
        for i in range(steps):
            # Linear interpolation
            t = i / (steps - 1) if steps > 1 else 0
            r = start_rgb[0] + (end_rgb[0] - start_rgb[0]) * t
            g = start_rgb[1] + (end_rgb[1] - start_rgb[1]) * t
            b = start_rgb[2] + (end_rgb[2] - start_rgb[2]) * t
            gradient.append(rgb_to_hex((r, g, b)))
            
        return gradient

    def display_welcome(self):
        """Display header with large ASCII art and smooth Halloween gradient."""
        if self.quiet_mode:
            return
        
        # Large ASCII art for HAUNTED - original block style
        ascii_art = [
            "██╗  ██╗ █████╗ ██╗   ██╗███╗   ██╗████████╗███████╗██████╗ ",
            "██║  ██║██╔══██╗██║   ██║████╗  ██║╚══██╔══╝██╔════╝██╔══██╗",
            "███████║███████║██║   ██║██╔██╗ ██║   ██║   █████╗  ██║  ██║",
            "██╔══██║██╔══██║██║   ██║██║╚██╗██║   ██║   ██╔══╝  ██║  ██║",
            "██║  ██║██║  ██║╚██████╔╝██║ ╚████║   ██║   ███████╗██████╔╝",
            "╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝   ╚═╝   ╚══════╝╚═════╝ ",
        ]
        
        # Generate smooth gradient: Bright Orange (#ff8c00) to Dark Red (#8b0000)
        gradient_colors = self.generate_gradient("#ff8c00", "#8b0000", len(ascii_art))
        
        # Print ASCII art with Halloween gradient
        self.console.print()
        for i, line in enumerate(ascii_art):
            art_text = Text()
            # Apply the calculated hex color for this line
            art_text.append(line, style=f"bold {gradient_colors[i]}")
            self.console.print(art_text)
        
        self.console.print()
        
        # Status line with current info
        status = Text()
        status.append("aura: ", style=STATUS_DIM)
        status.append("active", style=SUCCESS)
        status.append(" · ", style=DIM)
        status.append("spirit guide: ", style=STATUS_DIM)
        status.append(self.model_name, style=TEXT)
        status.append(" · ", style=DIM)
        status.append("v", style=STATUS_DIM)
        status.append(VERSION, style=STATUS_DIM)
        self.console.print(status)
        
        self.console.print()

    def command_preview(self, original_input: str, shell_command: str):
        """Display command preview with clean, minimal formatting."""
        self.console.print()
        
        # Thin, subtle rounded border
        border = "─" * 60
        self.console.print(f"╭{border}╮", style=DIM)
        
        # Original input with simple prefix
        input_text = Text()
        input_text.append("you: ", style=STATUS_DIM)
        input_text.append(original_input, style=TEXT)
        self.console.print(input_text)
        
        # Shell command with system prefix
        shell_text = Text()
        shell_text.append(SYSTEM_PREFIX + " ", style=STATUS_DIM)
        shell_text.append(shell_command, style=ACCENT)
        self.console.print(shell_text)
        
        self.console.print(f"╰{border}╯", style=DIM)
        self.console.print()
    
    def display_message(self, message: str, message_type: str = "info"):
        """Display a clean message with subtle prefix."""
        color = self._get_color_for_type(message_type)
        prefix = SYSTEM_PREFIX
        
        text = Text()
        text.append(prefix + " ", style=STATUS_DIM)
        text.append(message, style=color)
        self.console.print(text)
    
    def display_success(self, message: str = ""):
        """Display success message."""
        text = Text()
        text.append("✓ ", style=SUCCESS)
        text.append("SPELL CAST", style=SUCCESS)
        if message:
            text.append(" · ", style=DIM)
            text.append(message, style=TEXT)
        self.console.print(text)
    
    def display_error(self, message: str, hint: str = ""):
        """Display error message with clean formatting."""
        text = Text()
        text.append("✗ ", style=ERROR)
        text.append("error: ", style=ERROR)
        text.append(message, style=TEXT)
        self.console.print(text)
        
        if hint:
            # Multi-line hints with proper indentation
            for line in hint.split('\n'):
                hint_text = Text()
                if line.strip().startswith(('•', '1.', '2.', '3.')):
                    hint_text.append(line.strip(), style=STATUS_DIM)
                else:
                    hint_text.append(line.strip(), style=DIM)
                self.console.print(hint_text)
    
    def display_warning(self, message: str):
        """Display warning message."""
        text = Text()
        text.append("⚠ ", style=WARNING)
        text.append("OMEN: ", style=WARNING)
        text.append(message, style=TEXT)
        self.console.print(text)
    
    def display_result(self, stdout: str = "", stderr: str = "", exit_code: int = 0, execution_time: float = 0.0):
        """
        Display command execution result with clean formatting.
        
        Args:
            stdout: Standard output from command
            stderr: Standard error from command
            exit_code: Command exit code
            execution_time: Time taken to execute command
        """
        self.console.print()
        
        has_output = stdout and stdout.strip()
        
        # Requirement 6.3, 6.4: Always display exit code information for non-zero codes
        if exit_code == 0:
            # Pure success case
            self.display_success(f"{execution_time:.2f}s")
            
            if stdout:
                self.console.print()
                # Display output cleanly
                for line in stdout.strip().split('\n'):
                    self.console.print(f"{line}", style=TEXT)
                self.console.print()
        else:
            # Non-zero exit code - show error information
            # Hybrid approach: show output if available, but also indicate the error
            if has_output:
                # Command produced output but failed - show both
                self.display_warning(f"partial success (exit code {exit_code}) · {execution_time:.2f}s")
                
                self.console.print()
                # Display the output that was produced
                for line in stdout.strip().split('\n'):
                    self.console.print(f"{line}", style=TEXT)
                self.console.print()
                
                # Also show stderr if present
                if stderr:
                    self.console.print()
                    for line in stderr.strip().split('\n'):
                        self.console.print(f"{line}", style=ERROR)
            else:
                # True error case (no output and non-zero exit code)
                error_msg = f"command failed (exit code {exit_code})"
                hint = f"took {execution_time:.2f}s"
                self.display_error(error_msg, hint)
                
                if stderr:
                    self.console.print()
                    for line in stderr.strip().split('\n'):
                        self.console.print(f"{line}", style=ERROR)
        
        self.console.print()
    
    def loading_animation(self, message: str = "thinking"):
        """Return a context manager for subtle loading animation."""
        return LoadingAnimation(self.console, message)
    
    def display_ritual_start(self, ritual_name: str, total_steps: int):
        """Display ritual start banner."""
        self.console.print()
        text = Text()
        text.append("🔮 ", style=ACCENT)
        text.append(f"starting ritual: ", style=SECONDARY)
        text.append(ritual_name, style=SUCCESS)
        text.append(f" ({total_steps} steps)", style=STATUS_DIM)
        self.console.print(text)
        self.console.print()
    
    def display_ritual_step(self, step_num: int, total_steps: int, command: str, status: str):
        """Display ritual step with status."""
        if status == "running":
            icon = "⏳"
            style = STATUS_DIM
        elif status == "success":
            icon = "✓"
            style = SUCCESS
        else:  # failed
            icon = "✗"
            style = ERROR
        
        text = Text()
        text.append(f"  {icon} ", style=style)
        text.append(f"step {step_num}/{total_steps}: ", style=STATUS_DIM)
        text.append(command, style=TEXT)
        self.console.print(text)
    
    def display_ritual_complete(self, success: bool, total_time: float):
        """Display ritual completion banner."""
        self.console.print()
        if success:
            text = Text()
            text.append("✨ ", style=SUCCESS)
            text.append("ritual complete", style=SUCCESS)
            text.append(f" ({total_time:.1f}s)", style=STATUS_DIM)
            self.console.print(text)
        else:
            text = Text()
            text.append("✗ ", style=ERROR)
            text.append("ritual failed", style=ERROR)
            self.console.print(text)
        self.console.print()
    
    def prompt_confirmation(self, prompt_text: str = "execute?") -> str:
        """Display clean confirmation prompt."""
        text = Text()
        text.append(prompt_text + " ", style=STATUS_DIM)
        text.append("(y/n)", style=DIM)
        text.append(" ", style="")
        self.console.print(text, end='')
        return input()
    
    def get_input(self) -> str:
        """Get user input with Gemini-style bordered input box."""
        import sys
        import shutil
        
        # Get terminal width, default to 80 if can't detect
        try:
            term_width = shutil.get_terminal_size().columns
            border_width = min(term_width - 2, 80)  # Cap at 80, leave margin
        except Exception:
            border_width = 80
        
        # Top border with title
        title = " INVOCATION "
        available = border_width - 2 - len(title)
        if available < 0:
            # Fallback for very small terminals
            top_border = f"╭{'─' * (border_width - 2)}╮"
        else:
            left_len = available // 2
            right_len = available - left_len
            top_border = f"╭{'─' * left_len}[{ACCENT}]{title}[/{ACCENT}]{'─' * right_len}╮"
            
        self.console.print(top_border, style=DIM)
        
        # Middle line (pre-draw with spaces)
        # Padding logic: │ (1) + space (1) + › (1) + space (1) ... space + │ (1)
        # 4 chars prefix, 1 char suffix. Total 5 chars overhead.
        inner_space = border_width - 5
        middle_line = f"[{DIM}]│[/{DIM}] [{ACCENT}]{PROMPT_SYMBOL}[/{ACCENT}] {' ' * inner_space}[{DIM}]│[/{DIM}]"
        self.console.print(middle_line)

        # Bottom border
        bottom_border = f"╰{'─' * (border_width - 2)}╯"
        self.console.print(bottom_border, style=DIM)

        # Move cursor up 2 lines (to the middle line) and right 4 chars (past "│ › ")
        sys.stdout.write("\033[2A\r\033[4C")
        sys.stdout.flush()
        
        # Get user input
        # The user types over the spaces.
        user_input = input()

        # After Enter, cursor is on the bottom border line.
        # Move down one more line to ensure we don't overwrite the bottom border with next output
        sys.stdout.write("\n")
        sys.stdout.flush()

        # Optional: If user input was longer than the box, we might want to redraw the clean box 
        # properly truncated or expanded, but for now let's keep it simple.
        # If we want to guarantee the right border exists (in case they typed over it),
        # we can do a quick redraw like before, but let's see if this suffices.
        
        return user_input
    
    def display_status_bar(self, status: str = "ready", connection: str = "connected", hint: str = "press ? for help"):
        """Display persistent bottom status bar (Gemini-style)."""
        text = Text()
        text.append("─" * 60, style=DIM)
        self.console.print(text)
        
        status_text = Text()
        status_text.append("aura: ", style=STATUS_DIM)
        status_text.append(status, style=ACCENT)
        status_text.append(" · ", style=DIM)
        status_text.append("link: ", style=STATUS_DIM)
        status_text.append(connection, style=SUCCESS if connection == "connected" else WARNING)
        status_text.append(" · ", style=DIM)
        status_text.append(hint, style=DIM)
        self.console.print(status_text)
    
    def _get_color_for_type(self, message_type: str) -> str:
        """Get color for message type."""
        color_map = {
            "success": SUCCESS,
            "error": ERROR,
            "warning": WARNING,
            "info": TEXT,
            "processing": ACCENT
        }
        return color_map.get(message_type, TEXT)


class LoadingAnimation:
    """Context manager for cool, spooky loading animations."""
    
    def __init__(self, console: Console, message: str):
        self.console = console
        self.stop_event = threading.Event()
        self.thread = None
        
        # Start with the passed message, but we'll rotate immediately
        self.current_message = message
        
        # Use the 'moon' spinner for spooky vibes
        spinner_text = Text()
        spinner_text.append(message, style=STATUS_DIM)
        self.spinner = Spinner("moon", text=spinner_text)
        self.live = None
    
    def _rotate_phrases(self):
        """Thread function to rotate through spooky phrases."""
        while not self.stop_event.is_set():
            # Pick a random phrase
            phrase = random.choice(SPOOKY_PHRASES)
            
            # Create styled text
            text = Text()
            text.append(phrase, style=STATUS_DIM)
            
            # Update spinner text
            self.spinner.update(text=text)
            
            # Wait before next rotation
            self.stop_event.wait(1.5)
    
    def __enter__(self):
        """Start the animation."""
        # Start the live display
        self.live = Live(self.spinner, console=self.console, refresh_per_second=12)
        self.live.__enter__()
        
        # Start the phrase rotation thread
        self.thread = threading.Thread(target=self._rotate_phrases, daemon=True)
        self.thread.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Stop the animation."""
        # Signal thread to stop
        self.stop_event.set()
        if self.thread:
            self.thread.join(timeout=1.0)
            
        if self.live:
            self.live.__exit__(exc_type, exc_val, exc_tb)
        
        # Don't suppress KeyboardInterrupt - let it propagate
        if exc_type is KeyboardInterrupt:
            return False
        
        return False

    def display_ritual_start(self, ritual_name: str, total_steps: int):
        """Display ritual start banner."""
        self.console.print()
        border = "─" * 60
        self.console.print(f"╭{border}╮", style=SECONDARY)
        
        title = Text()
        title.append("  🔮 RITUAL: ", style=SECONDARY)
        title.append(ritual_name.upper(), style=ACCENT)
        self.console.print(title)
        
        info = Text()
        info.append(f"  {total_steps} steps to complete", style=STATUS_DIM)
        self.console.print(info)
        
        self.console.print(f"╰{border}╯", style=SECONDARY)
        self.console.print()
    
    def display_ritual_step(self, step_num: int, total_steps: int, command: str, status: str = "running"):
        """Display ritual step progress."""
        # Progress bar
        progress = "█" * step_num + "░" * (total_steps - step_num)
        progress_text = Text()
        progress_text.append(f"  [{step_num}/{total_steps}] ", style=STATUS_DIM)
        progress_text.append(progress, style=ACCENT if status == "running" else SUCCESS if status == "success" else ERROR)
        self.console.print(progress_text)
        
        # Step info
        if status == "running":
            icon = "⟳"
            color = ACCENT
        elif status == "success":
            icon = "✓"
            color = SUCCESS
        else:
            icon = "✗"
            color = ERROR
        
        step_text = Text()
        step_text.append(f"  {icon} ", style=color)
        step_text.append(command, style=TEXT if status == "running" else color)
        self.console.print(step_text)
        self.console.print()
    
    def display_ritual_complete(self, success: bool, total_time: float):
        """Display ritual completion banner."""
        self.console.print()
        border = "─" * 60
        self.console.print(f"╭{border}╮", style=SUCCESS if success else ERROR)
        
        if success:
            result = Text()
            result.append("  ✨ RITUAL COMPLETE ", style=SUCCESS)
            result.append(f"· {total_time:.2f}s", style=STATUS_DIM)
            self.console.print(result)
        else:
            result = Text()
            result.append("  ✗ RITUAL FAILED ", style=ERROR)
            result.append(f"· {total_time:.2f}s", style=STATUS_DIM)
            self.console.print(result)
        
        self.console.print(f"╰{border}╯", style=SUCCESS if success else ERROR)
        self.console.print()
