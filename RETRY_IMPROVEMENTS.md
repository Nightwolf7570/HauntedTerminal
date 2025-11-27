# Command Interpretation Improvements

## Problems Fixed

### 1. Retry Behavior Too Sensitive
The retry mechanism was too sensitive and would immediately add commands to the "bad commands" knowledge base (rejections table) when users pressed retry. This caused two issues:

- **Too aggressive rejection tracking**: Commands were marked as "bad" even when the user just wanted to try a different approach, not necessarily because the command was wrong.
- **Same command regeneration**: After retry, Ollama would sometimes generate the same command because the context hadn't changed enough, especially after restarting the CLI.

### 2. Invalid Command Syntax Not Caught
Ollama was generating invalid commands like `find ./ -type f \( -name "*.py" -o -mtime 7-14 \)` because:
- The `-mtime 7-14` syntax is invalid (should be `-mtime -7` for "last 7 days")
- The `-o` (OR) operator was incorrectly combining unrelated conditions
- No examples in the prompt showed correct time-based file searches

## Solution

### 1. Removed Premature Rejection Logging
**Changed behavior**: Rejections are now only logged when a command actually **fails** (exit code != 0), not when:
- User presses "retry" during confirmation
- User cancels with "no" during confirmation

**Rationale**: The rejection system should learn from actual command failures, not from user preferences or exploration.

### 2. Clear Rejections on Success
**New feature**: Added `clear_rejections()` method to `HistoryManager` that removes all rejections for a specific natural language input when a command succeeds.

**Benefit**: If a user retries and finds a working command, the system "forgets" the previous failed attempts, preventing them from polluting future suggestions.

### 3. Rejection Tracking Only on Execution Failure
**Changed behavior**: Commands are added to the rejections table only when:
- The command is executed
- The exit code is non-zero (failure)

**Code location**: `src/cli.py` line ~860

## Changes Made

### `src/cli.py` - Retry Behavior
1. Removed `history.add_rejection()` call when user presses "retry" during confirmation
2. Removed `history.add_rejection()` call when user cancels with "no"
3. Added `history.clear_rejections()` call when command succeeds (exit code 0)
4. Moved `history.add_rejection()` to only trigger on actual command failure (exit code != 0)

### `src/history.py` - Rejection Management
1. Added new method `clear_rejections(natural_language: str)` to remove all rejections for a specific input

### `src/ollama_client.py` - Better Command Generation
1. Added explicit guidance in system prompt about correct `-mtime` syntax:
   - `-mtime -7` means "modified in the last 7 days"
   - `-mtime +7` means "modified more than 7 days ago"
   - `-mtime 7` means "modified exactly 7 days ago"
   - Warning: NEVER use syntax like `-mtime 7-14` (invalid)
2. Added 4 new examples for time-based file searches in file operations domain
3. Added guidance to combine conditions with AND (implicit) not OR

## Testing
- All existing tests pass (23/23 in test_cli.py, 19/19 in test_history.py)
- Created `test_retry_behavior.py` to verify the new rejection clearing behavior
- No diagnostic issues found

## User Experience Improvements

### Retry Behavior
1. **Less aggressive learning**: The system won't "remember" commands as bad just because you wanted to try something different
2. **Better retry experience**: After finding a working command, previous failed attempts are cleared, so future similar requests won't be biased
3. **More exploration-friendly**: Users can freely retry without worrying about polluting the knowledge base

### Command Quality
1. **Correct time-based searches**: Ollama now generates valid `-mtime` syntax for file searches
2. **Better examples**: Domain-specific examples guide the LLM to generate more accurate commands
3. **Explicit warnings**: The prompt explicitly warns against common syntax errors like `-mtime 7-14`

## Example Fix
**Before:**
```bash
User: "Show me all python files I edited this week"
Ollama: find ./ -type f \( -name "*.py" -o -mtime 7-14 \) 2>/dev/null
# Invalid: -mtime 7-14 is not valid syntax, -o creates wrong logic
```

**After:**
```bash
User: "Show me all python files I edited this week"
Ollama: find . -type f -name "*.py" -mtime -7 2>/dev/null
# Correct: -mtime -7 means "last 7 days", conditions combined with AND
```
