#!/usr/bin/env python3
import re

pattern = r'(?<!2)>\s*/dev/(?!null)'

test_cases = [
    ('find . -name test 2>/dev/null', False),  # Should NOT match (safe)
    ('echo test >/dev/sda', True),              # Should match (dangerous)
    ('cat file 2>/dev/null', False),            # Should NOT match (safe)
    ('echo data >/dev/null', False),            # Should NOT match (safe - /dev/null is ok)
    ('echo data >/dev/sda1', True),             # Should match (dangerous)
]

print('Testing safety pattern:')
for cmd, should_match in test_cases:
    matches = bool(re.search(pattern, cmd))
    status = '✓' if matches == should_match else '✗'
    print(f'{status} {cmd:40} -> {"MATCH" if matches else "no match":10} (expected: {"MATCH" if should_match else "no match"})')
