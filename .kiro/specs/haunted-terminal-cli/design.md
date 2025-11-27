# Design Document

## Overview

The Haunted Terminal CLI is a Python application that bridges natural language understanding with system command execution through a local LLM. The architecture emphasizes safety, offline operation, and an engaging Halloween-themed user experience. The system uses Ollama with llama3.2 for command interpretation, typer for CLI framework, rich for terminal styling, subprocess for command execution, and SQLite for persistent command history.

## Architecture

The application follows a layered architecture with clear separation of concerns:

1. **Presentation Layer**: CLI interface using typer and rich for themed input/output
2. **Application Layer**: Command orchestration, confirmation flows, and safety checks
3. **LLM Integration Layer**: Ollama client for natural language interpretation
4. **Execution Layer**: Subprocess wrapper for safe command execution
5. **Persistence Layer**: SQLite database for command history and suggestions

The main execution flow:
```
User Input → NL Interpretation (Ollama) → Safety Check → User Confirmation → Command Execution → Themed Output → History Storage
```

## Components and Interfaces

### 1. CLI Interface (`cli.py`)
- **Responsibility**: Handle user interaction, display themed output
- **Dependencies**: typer, rich
- **Key Methods**:
  - `main()`: Entry point, initialize app and start REPL loop
  - `display_welcome()`: Show themed banner
  - `get_user_input()`: Prompt for natural language command
  - `display_command_preview()`: Show interpreted command with theme
  - `display_output()`: Render command results with spooky styling

### 2. Theme Manager (`theme.py`)
- **Responsibility**: Centralize all styling and themed messages
- **Dependencies**: rich
- **Key Components**:
  - Color palette: purple (#9D4EDD), orange (#FF6D00), green (#06FFA5)
  - Gothic borders and mystical symbols (🔮, 👻, 🎃, ⚡)
  - Message templates for success, error, warning states
  - Rich console styling configurations



### 3. Ollama Client (`ollama_client.py`)
- **Responsibility**: Interface with local Ollama service
- **Dependencies**: requests (for HTTP API calls to Ollama)
- **Key Methods**:
  - `check_connection()`: Verify Ollama is running
  - `interpret_command(natural_language: str) -> str`: Send NL to Ollama, get shell command
  - `build_prompt(user_input: str) -> str`: Construct system prompt for command interpretation with enhanced domain-specific examples
  - `_get_domain_examples(user_input: str) -> str`: Analyze input and return relevant domain-specific examples
- **Configuration**:
  - Default endpoint: `http://localhost:11434`
  - Model: `llama3.2`
  - Timeout: 10 seconds
- **Enhanced Prompt Strategy**:
  - Categorize user intent (file ops, process mgmt, network, text processing)
  - Include 3-5 relevant examples per detected category
  - Emphasize proper quoting, error suppression, and safe defaults
  - Provide macOS-specific guidance when applicable

### 4. Command Executor (`executor.py`)
- **Responsibility**: Execute shell commands safely
- **Dependencies**: subprocess
- **Key Methods**:
  - `execute(command: str) -> ExecutionResult`: Run command and capture output
  - `is_destructive(command: str) -> bool`: Check if command is dangerous
  - `validate_syntax(command: str) -> bool`: Basic command validation
- **ExecutionResult Model**:
  - `stdout: str`
  - `stderr: str`
  - `exit_code: int`
  - `execution_time: float`

### 5. Safety Manager (`safety.py`)
- **Responsibility**: Identify and handle destructive operations
- **Key Methods**:
  - `classify_command(command: str) -> CommandRisk`: Determine risk level
  - `get_confirmation(command: str, risk: CommandRisk) -> bool`: Prompt user appropriately
  - `DESTRUCTIVE_PATTERNS`: List of regex patterns for dangerous commands
- **CommandRisk Enum**: SAFE, MODERATE, DESTRUCTIVE

### 6. History Manager (`history.py`)
- **Responsibility**: Persist and retrieve command history
- **Dependencies**: sqlite3
- **Key Methods**:
  - `initialize_db()`: Create database schema if needed
  - `save_command(nl_input: str, shell_cmd: str, result: ExecutionResult)`: Store successful command
  - `get_suggestions(nl_input: str, limit: int) -> List[HistoryEntry]`: Retrieve similar past commands
  - `get_recent_commands(limit: int) -> List[HistoryEntry]`: Get recent history
- **Database Schema**:
  ```sql
  CREATE TABLE command_history (
    id INTEGER PRIMARY KEY,
    natural_language TEXT,
    shell_command TEXT,
    working_directory TEXT,
    exit_code INTEGER,
    timestamp DATETIME,
    execution_time REAL
  )
  ```

## Data Models

### CommandRequest
```python
@dataclass
class CommandRequest:
    natural_language: str
    timestamp: datetime
    working_directory: str
```

### CommandInterpretation
```python
@dataclass
class CommandInterpretation:
    original_input: str
    shell_command: str
    risk_level: CommandRisk
    confidence: float  # From Ollama if available
```

### ExecutionResult
```python
@dataclass
class ExecutionResult:
    command: str
    stdout: str
    stderr: str
    exit_code: int
    execution_time: float
    timestamp: datetime
```

### HistoryEntry
```python
@dataclass
class HistoryEntry:
    id: int
    natural_language: str
    shell_command: str
    working_directory: str
    exit_code: int
    timestamp: datetime
    execution_time: float
```



## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Input length validation
*For any* user input string, if the length is between 1 and 1000 characters, the system should accept it; if empty or over 1000 characters, the system should reject it with appropriate messaging.
**Validates: Requirements 1.2, 1.3**

### Property 2: Session history persistence
*For any* sequence of commands executed in a session, querying the session history should return all executed commands in chronological order.
**Validates: Requirements 1.5**

### Property 3: Ollama request formation
*For any* valid natural language input, the system should construct and send a properly formatted request to the local Ollama endpoint.
**Validates: Requirements 2.1**

### Property 4: Timeout enforcement
*For any* Ollama request, if the response time exceeds 10 seconds, the system should timeout and display an error message.
**Validates: Requirements 2.2**

### Property 5: Command syntax validation
*For any* command string returned by Ollama, the system should validate basic shell syntax before presenting it to the user.
**Validates: Requirements 2.5**

### Property 6: Command preview completeness
*For any* interpreted command, the preview display should contain both the original natural language input and the shell command, and should prompt for user confirmation.
**Validates: Requirements 3.1, 3.2, 3.3**

### Property 7: Destructive command classification
*For any* shell command string, if it contains patterns matching rm, mv, dd, format, or mkfs, the system should classify it as destructive.
**Validates: Requirements 4.1, 4.5**

### Property 8: Destructive command warning
*For any* command classified as destructive, the system should display a prominent warning and require explicit typed confirmation beyond yes/no.
**Validates: Requirements 4.2, 4.3**

### Property 9: Cancellation safety
*For any* destructive command that is cancelled by the user, the system should not execute the command, should log the cancellation, and should return to the input prompt.
**Validates: Requirements 4.4**

### Property 10: Success message theming
*For any* successfully executed command, the displayed success message should contain themed language elements (magical, mystical references).
**Validates: Requirements 5.3**

### Property 11: Error message helpfulness
*For any* failed command, the error message should contain both themed elements and helpful troubleshooting information.
**Validates: Requirements 5.4**

### Property 12: Output stream capture
*For any* executed command, the system should capture and make available both stdout and stderr streams.
**Validates: Requirements 6.2**

### Property 13: Result display with exit codes
*For any* completed command, the display should show the output and, if the exit code is non-zero, should prominently display the exit code with error information.
**Validates: Requirements 6.3, 6.4**

### Property 14: Working directory preservation
*For any* sequence of commands, the working directory context should be preserved across executions unless explicitly changed by a command.
**Validates: Requirements 6.5**

### Property 15: Error recovery
*For any* exception or error that occurs, the system should catch it, display a themed error message, log details, and return to the main input prompt without crashing.
**Validates: Requirements 7.1, 7.4, 7.5**

### Property 16: Failed command stderr display
*For any* command that fails during execution, the system should display the stderr output along with helpful context.
**Validates: Requirements 7.3**

### Property 17: Local-only operation
*For any* command processing operation, the system should make network requests only to localhost (Ollama endpoint) and never to external services.
**Validates: Requirements 8.1, 8.2**

### Property 18: Command persistence
*For any* successfully executed command, the system should persist a record containing the natural language input, shell command, timestamp, working directory, exit code, and execution time to the SQLite database.
**Validates: Requirements 11.1, 11.2**

### Property 19: History-based suggestions
*For any* natural language input, if similar commands exist in history, the system should retrieve and display relevant suggestions ranked by recency and frequency.
**Validates: Requirements 11.3, 11.4**

### Property 20: Domain-specific example inclusion
*For any* natural language input that matches a command category (file, process, network, text), the generated prompt should include relevant domain-specific examples for that category.
**Validates: Requirements 12.1, 12.2, 12.3, 12.4, 12.5**

### Property 21: Safe interpretation preference
*For any* ambiguous natural language input, the system should generate commands that favor non-destructive operations and include appropriate error suppression.
**Validates: Requirements 12.8**



## Error Handling

### Error Categories

1. **Ollama Connection Errors**
   - Detection: HTTP connection failures, timeouts
   - Response: Display troubleshooting message with steps to start Ollama
   - Recovery: Return to input prompt, allow retry

2. **Command Interpretation Errors**
   - Detection: Empty response, invalid JSON, nonsense output from Ollama
   - Response: Display themed error asking user to rephrase
   - Recovery: Return to input prompt

3. **Command Execution Errors**
   - Detection: Non-zero exit codes, subprocess exceptions
   - Response: Display stderr with themed formatting and exit code
   - Recovery: Return to input prompt, log to history with failure status

4. **Database Errors**
   - Detection: SQLite exceptions during read/write
   - Response: Log error, display warning, continue without history features
   - Recovery: Graceful degradation - app continues without persistence

5. **Validation Errors**
   - Detection: Input too long, empty input, invalid command syntax
   - Response: Display themed validation message
   - Recovery: Re-prompt for input

### Error Handling Strategy

- All exceptions caught at the main loop level
- Specific handlers for known error types
- Generic handler for unexpected errors
- All errors logged with full stack traces
- User-facing messages are themed and helpful
- Application never crashes - always returns to prompt

## Testing Strategy

### Unit Testing

The application will use pytest for unit testing. Unit tests will cover:

- **Theme Manager**: Verify message templates contain required elements
- **Safety Manager**: Test destructive pattern matching with specific examples
- **Ollama Client**: Mock Ollama responses to test parsing logic
- **Command Executor**: Test with safe commands (echo, ls) to verify output capture
- **History Manager**: Test database operations with in-memory SQLite

Example unit tests:
- Test that "rm -rf /" is classified as destructive
- Test that empty input is rejected
- Test that database schema is created correctly
- Test that Ollama connection errors are handled gracefully

### Property-Based Testing

The application will use Hypothesis for property-based testing. Property tests will verify universal behaviors across many inputs:

**Configuration**: Each property test will run a minimum of 100 iterations.

**Tagging**: Each property-based test will include a comment with this format:
```python
# Feature: haunted-terminal-cli, Property {number}: {property_text}
```

**Property Test Coverage**:
- Property 1: Input length validation with random strings
- Property 7: Destructive command classification with generated command strings
- Property 12: Output stream capture with various commands
- Property 14: Working directory preservation across command sequences
- Property 18: Command persistence with random command data
- Property 19: History suggestions with generated history and queries

Example property test structure:
```python
@given(st.text(min_size=1, max_size=1000))
def test_valid_input_accepted(input_text):
    # Feature: haunted-terminal-cli, Property 1: Input length validation
    result = validate_input(input_text)
    assert result.is_valid == True
```

### Integration Testing

Integration tests will verify end-to-end flows:
- Start app → enter command → verify Ollama called → confirm → verify execution
- Test with Ollama running locally
- Test offline operation (no external network calls)
- Test database persistence across app restarts

### Testing Approach

1. **Implementation-first development**: Implement features before writing tests
2. **Complementary coverage**: Unit tests catch specific bugs, property tests verify general correctness
3. **Real dependencies**: Use actual Ollama and SQLite where possible, minimal mocking
4. **Safety testing**: Extensive testing of destructive command detection without actually running dangerous commands



## Visual Design Specification

### Design Philosophy

The Haunted Terminal should feel like a possessed computer terminal. Visual effects should suggest:
- Digital corruption and glitching
- Spirits interfering with normal terminal operation
- Reality breaking through the screen
- Ominous but controlled chaos

NOT campy Halloween decorations. Think: creepy tech horror.

### Welcome Banner

On startup, display a large ASCII art banner (15-25 lines) showing a skull or ghostly face emerging from terminal lines:
- Use color gradient: purple → orange → green
- Include glitch effects (random characters that quickly correct)
- Feel ominous but polished

Below the banner, display system info in corrupted style:
```
> SYSTEM.STATUS............HAUNTED
> SHELL.TYPE...............CURSED
> SECURITY.LEVEL...........BREACHED
> SPIRITS.ACTIVE...........YES
```

Effect: On first render, some characters appear as random symbols (█, ▓, ░) then "resolve" to correct text after 0.5 seconds.

**CRITICAL**: No boxes, no frames, no borders. Clean lines only.

### Separator Styles

**Standard Output** (for command results):
```
═══════════════════════════════════════
  Content goes here
═══════════════════════════════════════
```
- Color: Purple separators, white text
- Add slight "drip" effect: Occasional characters extend below bottom line

**Command Preview** (before execution):
```
    ◈─────────────────────────────◈
    ✦ THE SPIRITS DIVINE...
    
    Input: "find python files"
    Shell: find . -name "*.py"
    
    ◈─────────────────────────────◈
    Summon this spell? Y/n _
```
- Color: Orange/purple gradient on separators
- Pulsing glow effect on the ◈ symbols
- No brackets around Y/n prompt

**Error Display** (for failures):
```
═════════════════════════════════════
⚠  CORRUPTION DETECTED  ⚠
═════════════════════════════════════
The ritual failed: [error message]

The spirits suggest: [hint]
═════════════════════════════════════
```
- Color: Red text on dark background
- Glitch effect: Separator characters briefly scramble then restore
- Broken appearance: some ═ become ─ or ░

### Loading States & Animations

**While Ollama is Processing**:
Animated sequence (cycle through frames every 0.2 seconds):
```
Frame 1: 🔮 Consulting the spirits...
Frame 2: 🔮 Consulting the spirits..
Frame 3: 🔮 Consulting the spirits.
Frame 4: 🔮 Consulting the spirits
Frame 5: 🔮 C̴o̷n̶s̸u̵l̷t̶i̷n̶g̷ the spirits... (glitch effect)
Frame 6: 🔮 Consulting the spirits...
```

**Execution Progress** (for long-running commands):
```
████████████░░░░░░░░ Summoning... 60%
```
- Color: Green fill, purple empty
- Glitch: Occasionally a filled block becomes ▓ briefly
- No brackets or framing characters

### Symbol Usage Guide

| Message Type | Symbol | Color |
|--------------|--------|-------|
| Success | 🎃 | Green |
| Error | 💀 | Red |
| Warning | ⚡ | Orange |
| Info | 👻 | Purple |
| Processing | 🔮 | Pulsing purple/white |
| Confirmation | ✦ | Orange |

Placement: Always at start of message line, followed by space.

### Text Effects

**Glitch Effect** (for dramatic moments):
Temporarily replace text with corrupted characters, then restore:
- Normal: "Command executed"
- Glitched: "C̴o̷m̶m̸a̵n̷d̶ ̷e̶x̸e̵c̷u̶t̷e̶d̷"
- Duration: 0.3 seconds, then restore

**Fade-in Effect** (for results):
- Display output line by line with slight delay (0.05s per line)
- Creates "materializing from the void" effect

**Typing Effect** (for prompts):
- Simulate character-by-character typing for dramatic prompts
- Speed: 0.03s per character

### Color Palette

Primary colors:
- Purple: `#9D4EDD` (mystical, primary UI)
- Orange: `#FF6D00` (warnings, highlights)
- Green: `#06FFA5` (success, active elements)

Secondary colors:
- Red: `#FF0054` (errors, danger)
- White: `#FFFFFF` (primary text)
- Dark Gray: `#1A1A1A` (background)

### Implementation Notes

- Use `rich.console.Console` for all output
- Use `rich.text.Text` for styled strings
- Use `rich.live.Live` for animations
- Use `rich.progress.Progress` for progress bars
- Implement glitch effects with timed character replacement
- Cache ASCII art to avoid regeneration
- Ensure all effects are performant (no lag in terminal)
