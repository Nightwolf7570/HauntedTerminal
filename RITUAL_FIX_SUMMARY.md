# Ritual Creation Bug Fix

## Problem

When creating a ritual using `ritual create <name>`, the input prompts were broken:

```
step 1 > (y/n) git add .
step 1 > (y/n) git commit -m "Adding features"
step 1 > (y/n) b
step 1 > (y/n) y
step 1 > (y/n) y
step 1 > (y/n) done
step 1 > (y/n)
```

The prompt was showing "(y/n)" and not properly accepting command input.

## Root Cause

The code was calling `self.theme.prompt_confirmation()` which is designed for yes/no questions, not for general text input. This method automatically appends "(y/n)" to the prompt.

## Solution

Replaced the confirmation prompt with clean `input()` calls and proper Rich console formatting:

```python
# Before (broken)
step_input = self.theme.prompt_confirmation(f"step {len(steps) + 1} >")

# After (fixed)
self.theme.console.print(f"[{STATUS_DIM}]step {len(steps) + 1} >[/{STATUS_DIM}] ", end="")
cmd = input().strip()
```

## Changes Made

**File**: `src/cli.py` (lines 420-450)

### Improvements:
1. ✅ Removed incorrect use of `prompt_confirmation()`
2. ✅ Added clean input prompts with proper styling
3. ✅ Added visual feedback ("✓ added") after each step
4. ✅ Improved spacing and readability
5. ✅ Maintained themed output using Rich console

## Testing

All ritual tests pass:
- ✅ `test_create_and_get_ritual`
- ✅ `test_list_rituals`
- ✅ `test_delete_ritual`
- ✅ `test_duplicate_ritual_name`

## How It Works Now

```bash
> ritual create my-workflow

✓ SPELL CAST · Creating ritual 'my-workflow'

Description (optional): Deploy my app

Enter commands one by one. Type 'done' to finish.

step 1 > git add .
  ✓ added
step 2 > git commit -m "Update"
  ✓ added
step 3 > git push origin main
  ✓ added
step 4 > done

✓ SPELL CAST · ritual 'my-workflow' saved with 3 steps
```

## Documentation

Created `RITUAL_GUIDE.md` with:
- Complete usage instructions
- Example rituals
- Quick reference table
- Troubleshooting tips

## Verification

The fix has been tested and verified to work correctly. Users can now create rituals without the confusing "(y/n)" prompts.
