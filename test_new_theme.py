#!/usr/bin/env python3
"""
Quick visual test of the new clean, modern theme.
"""

from src.theme import ThemeManager

def test_theme():
    """Test all theme elements."""
    theme = ThemeManager()
    
    print("\n" + "="*70)
    print("HAUNTED TERMINAL - NEW CLEAN THEME TEST")
    print("="*70 + "\n")
    
    # 1. Welcome header
    print("1. Welcome Header:")
    theme.display_welcome()
    
    # 2. Command preview
    print("2. Command Preview:")
    theme.command_preview("list all python files", "find . -name '*.py'")
    
    # 3. Success message
    print("3. Success Message:")
    theme.display_success("connected to ollama")
    print()
    
    # 4. Error message
    print("4. Error Message:")
    theme.display_error("cannot connect to ollama", "check if ollama is running: 'ollama serve'")
    print()
    
    # 5. Warning message
    print("5. Warning Message:")
    theme.display_warning("command cancelled")
    print()
    
    # 6. Result display (success)
    print("6. Success Result:")
    theme.display_result(
        stdout="file1.py\nfile2.py\nfile3.py",
        exit_code=0,
        execution_time=0.23
    )
    
    # 7. Result display (error)
    print("7. Error Result:")
    theme.display_result(
        stderr="command not found: invalid",
        exit_code=127,
        execution_time=0.05
    )
    
    # 8. Status bar
    print("8. Status Bar:")
    theme.display_status_bar(status="ready", connection="connected", hint="press ? for help")
    print()
    
    # 9. Input prompt
    print("9. Input Prompt (visual only, not interactive):")
    print("› [user would type here]")
    print()
    
    print("="*70)
    print("Theme test complete! All elements displayed successfully.")
    print("="*70 + "\n")

if __name__ == "__main__":
    test_theme()
