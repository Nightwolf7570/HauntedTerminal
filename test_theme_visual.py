#!/usr/bin/env python3
"""
Visual test for the updated Haunted Terminal theme.
Tests the new dark, muted color palette and centered text.
"""

from src.theme import ThemeManager

def main():
    theme = ThemeManager()
    
    print("\n" + "="*80)
    print("HAUNTED TERMINAL THEME - VISUAL TEST")
    print("Dark, Muted, Faded CRT Aesthetic")
    print("="*80 + "\n")
    
    # Test welcome banner
    print("1. Welcome Banner (centered):")
    theme.display_welcome()
    
    print("\n" + "-"*80 + "\n")
    
    # Test command preview
    print("2. Command Preview (centered):")
    theme.command_preview_separator("list all python files", "find . -name '*.py'")
    
    print("\n" + "-"*80 + "\n")
    
    # Test success message
    print("3. Success Message (centered):")
    theme.display_success("Command executed in 0.5 seconds")
    
    print("\n" + "-"*80 + "\n")
    
    # Test error message
    print("4. Error Message (centered):")
    theme.display_error("Command not found", "Try checking your spelling")
    
    print("\n" + "-"*80 + "\n")
    
    # Test warning
    print("5. Warning Message (centered):")
    theme.display_warning("This command may be destructive")
    
    print("\n" + "-"*80 + "\n")
    
    # Test standard separator
    print("6. Standard Separator (centered):")
    theme.standard_separator("Command Output")
    
    print("\n" + "-"*80 + "\n")
    
    # Test error separator
    print("7. Error Separator (centered):")
    theme.error_separator("Connection timeout", "Check if Ollama is running")
    
    print("\n" + "-"*80 + "\n")
    
    # Test different message types
    print("8. Various Message Types (centered):")
    theme.display_message("Processing your request...", "processing")
    theme.display_message("Information message", "info")
    theme.display_message("Success!", "success")
    
    print("\n" + "="*80)
    print("Theme test complete!")
    print("="*80 + "\n")

if __name__ == "__main__":
    main()
