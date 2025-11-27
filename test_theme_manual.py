#!/usr/bin/env python3
"""
Manual test script for theme manager.
Run this to visually verify the theme components.
"""

from src.theme import ThemeManager
import time

def test_theme():
    theme = ThemeManager()
    
    print("\n=== Testing Welcome Banner ===")
    theme.display_welcome()
    time.sleep(1)
    
    print("\n=== Testing Standard Separator ===")
    theme.standard_separator("This is standard output")
    time.sleep(1)
    
    print("\n=== Testing Command Preview ===")
    theme.command_preview_separator(
        "list all python files",
        "find . -name '*.py'"
    )
    time.sleep(1)
    
    print("\n=== Testing Error Separator ===")
    theme.error_separator(
        "Command not found",
        "Try checking your spelling"
    )
    time.sleep(1)
    
    print("\n=== Testing Message Types ===")
    theme.display_message("This is an info message", "info")
    theme.display_message("This is a warning", "warning")
    theme.display_message("This is an error", "error")
    theme.display_message("This is a success", "success")
    time.sleep(1)
    
    print("\n=== Testing Success Display ===")
    theme.display_success("Command executed successfully")
    time.sleep(1)
    
    print("\n=== Testing Error Display ===")
    theme.display_error("Something went wrong", "Try running with sudo")
    time.sleep(1)
    
    print("\n=== Testing Warning Display ===")
    theme.display_warning("This operation is destructive!")
    time.sleep(1)
    
    print("\n=== Testing Glitch Effect ===")
    theme.glitch_effect("Command executed successfully")
    time.sleep(1)
    
    print("\n=== Testing Fade-in Effect ===")
    lines = ["Line 1", "Line 2", "Line 3", "Line 4"]
    theme.fade_in_effect(lines, delay=0.1)
    time.sleep(1)
    
    print("\n=== Testing Typing Effect ===")
    theme.typing_effect("The spirits are watching...", speed=0.05)
    time.sleep(1)
    
    print("\n=== Testing Loading Animation ===")
    with theme.loading_animation("Consulting the spirits"):
        time.sleep(2)
    print("\nAnimation complete!")
    
    print("\n=== Testing Progress Bar ===")
    progress = theme.progress_bar(100, "Summoning")
    task = progress.add_task("Summoning", total=100)
    progress.start()
    for i in range(100):
        progress.update(task, advance=1)
        time.sleep(0.02)
    progress.stop()
    
    print("\n=== All Tests Complete ===")

if __name__ == "__main__":
    test_theme()
