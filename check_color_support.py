
from rich.console import Console
from rich.text import Text
import os
import sys

console = Console()

def check_colors():
    print(f"Terminal: {os.environ.get('TERM')}")
    print(f"ColorTerm: {os.environ.get('COLORTERM')}")
    print(f"Rich Console System: {console.color_system}")
    
    # Define the colors from theme.py
    colors = {
        "BACKGROUND": "#0f1015",
        "ACCENT": "#06b6d4",
        "SECONDARY": "#a78bfa",
        "TEXT": "#e5e7eb",
        "DIM": "#6b7280",
        "STATUS_DIM": "#4d7c7c",
        "SUCCESS": "#10b981",
        "ERROR": "#ef4444",
        "WARNING": "#f59e0b"
    }

    print("\nColor Test:")
    for name, hex_val in colors.items():
        # Print a block of the color and the text
        console.print(f"[{hex_val}]██████[/{hex_val}] {name} ({hex_val})")

if __name__ == "__main__":
    check_colors()
