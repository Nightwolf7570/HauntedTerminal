#!/usr/bin/env python3
"""
Quick test script for theme manager - no animations.
"""

from src.theme import ThemeManager

def test_theme():
    theme = ThemeManager()
    
    print("\n=== Testing Welcome Banner ===")
    theme.display_welcome()
    
    print("\n=== Testing Standard Separator ===")
    theme.standard_separator("This is standard output")
    
    print("\n=== Testing Command Preview ===")
    theme.command_preview_separator(
        "list all python files",
        "find . -name '*.py'"
    )
    
    print("\n=== Testing Error Separator ===")
    theme.error_separator(
        "Command not found",
        "Try checking your spelling"
    )
    
    print("\n=== Testing Message Types ===")
    theme.display_message("This is an info message", "info")
    theme.display_message("This is a warning", "warning")
    theme.display_message("This is an error", "error")
    theme.display_message("This is a success", "success")
    
    print("\n=== Testing Success Display ===")
    theme.display_success("Command executed successfully")
    
    print("\n=== Testing Error Display ===")
    theme.display_error("Something went wrong", "Try running with sudo")
    
    print("\n=== Testing Warning Display ===")
    theme.display_warning("This operation is destructive!")
    
    print("\n=== Testing Glitch Effect ===")
    theme.glitch_effect("Command executed successfully")
    
    print("\n=== Testing Fade-in Effect ===")
    lines = ["Line 1", "Line 2", "Line 3"]
    theme.fade_in_effect(lines, delay=0.05)
    
    print("\n=== Testing Typing Effect ===")
    theme.typing_effect("The spirits are watching...", speed=0.02)
    
    print("\n=== All Tests Complete ===")

if __name__ == "__main__":
    test_theme()
