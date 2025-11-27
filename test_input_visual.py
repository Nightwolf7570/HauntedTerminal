#!/usr/bin/env python3
"""Visual test of input box."""

from src.theme import ThemeManager

theme = ThemeManager()

print("=" * 80)
print("BEFORE INPUT BOX")
print("=" * 80)
print()

result = theme.get_input()

print()
print("=" * 80)
print("AFTER INPUT BOX")
print("=" * 80)
print(f"You entered: '{result}'")
