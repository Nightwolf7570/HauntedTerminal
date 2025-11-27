#!/usr/bin/env python3
"""Test the input box rendering."""

from src.theme import ThemeManager

def test_input_box():
    """Test the bordered input box."""
    theme = ThemeManager()
    
    print("Testing input box - type something and press Enter:")
    print()
    
    user_input = theme.get_input()
    
    print()
    print(f"You entered: {user_input}")
    print()

if __name__ == "__main__":
    test_input_box()
