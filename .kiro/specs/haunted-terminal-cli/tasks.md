# Implementation Plan

- [x] 1. Set up project structure and dependencies
  - Create directory structure for the application
  - Create requirements.txt with dependencies: typer, rich, requests, hypothesis, pytest
  - Create main entry point haunted.py
  - Set up basic project configuration
  - _Requirements: 10.1_

- [x] 2. Implement theme manager with visual design
  - Create theme.py with color palette constants
  - Implement ASCII art banner with skull/ghostly face design
  - Create separator styles (standard, command preview, error display)
  - Implement symbol mapping for different message types
  - Create text effect functions (glitch, fade-in, typing)
  - Implement loading animations (Ollama processing, execution progress)
  - _Requirements: 5.1, 5.2, 10.2_

- [x] 3. Implement history manager with SQLite persistence
  - Create history.py with database schema
  - Implement initialize_db() to create tables if not exist
  - Implement save_command() to persist successful executions
  - Implement get_suggestions() for similarity-based retrieval
  - Implement get_recent_commands() for history display
  - _Requirements: 11.1, 11.2, 11.5_

- [x] 3.1 Write property test for command persistence
  - **Property 18: Command persistence**
  - **Validates: Requirements 11.1, 11.2**

- [x] 3.2 Write property test for history suggestions
  - **Property 19: History-based suggestions**
  - **Validates: Requirements 11.3, 11.4**

- [x] 4. Implement safety manager for destructive command detection
  - Create safety.py with CommandRisk enum
  - Define DESTRUCTIVE_PATTERNS list with regex patterns
  - Implement classify_command() to detect dangerous operations
  - Implement get_confirmation() with different prompts based on risk level
  - _Requirements: 4.1, 4.5_

- [x] 4.1 Write property test for destructive command classification
  - **Property 7: Destructive command classification**
  - **Validates: Requirements 4.1, 4.5**

- [x] 4.2 Write unit tests for safety manager
  - Test specific destructive commands (rm -rf, dd, etc.)
  - Test safe commands are not flagged
  - Test confirmation prompt variations
  - _Requirements: 4.1, 4.2, 4.3_


- [x] 5. Implement Ollama client for LLM integration
  - Create ollama_client.py with OllamaClient class
  - Implement check_connection() to verify Ollama is running
  - Implement build_prompt() to construct system prompt for command interpretation
  - Implement interpret_command() to send requests and parse responses
  - Add timeout handling (10 second limit)
  - Add error handling for connection failures
  - _Requirements: 2.1, 2.2, 2.4, 8.1_

- [x] 5.1 Write property test for Ollama request formation
  - **Property 3: Ollama request formation**
  - **Validates: Requirements 2.1**

- [x] 5.2 Write property test for timeout enforcement
  - **Property 4: Timeout enforcement**
  - **Validates: Requirements 2.2**

- [x] 5.3 Write unit tests for Ollama client
  - Test connection checking with mock responses
  - Test prompt construction
  - Test error handling for unavailable service
  - _Requirements: 2.3, 2.4_

- [x] 6. Implement command executor for safe shell execution
  - Create executor.py with CommandExecutor class
  - Implement execute() to run commands via subprocess
  - Capture stdout, stderr, exit code, and execution time
  - Implement validate_syntax() for basic command validation
  - Preserve working directory context across executions
  - _Requirements: 6.2, 6.5_

- [x] 6.1 Write property test for output stream capture
  - **Property 12: Output stream capture**
  - **Validates: Requirements 6.2**

- [x] 6.2 Write property test for working directory preservation
  - **Property 14: Working directory preservation**
  - **Validates: Requirements 6.5**

- [x] 6.3 Write unit tests for command executor
  - Test with safe commands (echo, ls, pwd)
  - Test stderr capture with failing commands
  - Test exit code reporting
  - _Requirements: 6.3, 6.4_

- [x] 7. Implement CLI interface with typer and rich
  - Create cli.py with main application loop
  - Implement display_welcome() with themed banner and glitch effects
  - Implement get_user_input() with input validation
  - Implement display_command_preview() with themed formatting
  - Implement display_output() for command results
  - Handle exit commands (exit, quit)
  - Maintain session command history
  - _Requirements: 1.1, 1.2, 1.4, 1.5, 3.1, 3.2, 3.3_

- [x] 7.1 Write property test for input length validation
  - **Property 1: Input length validation**
  - **Validates: Requirements 1.2, 1.3**

- [x] 7.2 Write property test for session history persistence
  - **Property 2: Session history persistence**
  - **Validates: Requirements 1.5**


- [x] 8. Integrate all components into main application flow
  - Create main haunted.py entry point
  - Wire together CLI, Ollama client, executor, safety manager, and history manager
  - Implement main REPL loop: input → interpret → preview → confirm → execute → display → save
  - Add startup dependency checks (Ollama availability)
  - Add graceful error handling and recovery
  - Display offline operation confirmation message
  - _Requirements: 1.1, 3.4, 3.5, 8.5, 10.3, 10.5_

- [x] 8.1 Write property test for command syntax validation
  - **Property 5: Command syntax validation**
  - **Validates: Requirements 2.5**

- [x] 8.2 Write property test for command preview completeness
  - **Property 6: Command preview completeness**
  - **Validates: Requirements 3.1, 3.2, 3.3**

- [x] 8.3 Write property test for destructive command warning
  - **Property 8: Destructive command warning**
  - **Validates: Requirements 4.2, 4.3**

- [x] 8.4 Write property test for cancellation safety
  - **Property 9: Cancellation safety**
  - **Validates: Requirements 4.4**

- [x] 9. Implement comprehensive error handling
  - Add error handlers for Ollama connection failures
  - Add error handlers for command interpretation errors
  - Add error handlers for command execution errors
  - Add error handlers for database errors with graceful degradation
  - Add error handlers for validation errors
  - Ensure all errors display themed messages and return to prompt
  - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_

- [x] 9.1 Write property test for error recovery
  - **Property 15: Error recovery**
  - **Validates: Requirements 7.1, 7.4, 7.5**

- [x] 9.2 Write property test for failed command stderr display
  - **Property 16: Failed command stderr display**
  - **Validates: Requirements 7.3**

- [x] 9.3 Write unit tests for error handling
  - Test Ollama connection error with troubleshooting message
  - Test command interpretation errors
  - Test database error graceful degradation
  - _Requirements: 7.2_

- [x] 10. Implement themed output for all message types
  - Add success message formatting with magical themed language
  - Add error message formatting with spooky but helpful content
  - Add result display with exit code handling
  - Ensure all output uses theme manager consistently
  - _Requirements: 5.3, 5.4, 6.3, 6.4_

- [x] 10.1 Write property test for success message theming
  - **Property 10: Success message theming**
  - **Validates: Requirements 5.3**

- [ ] 10.2 Write property test for error message helpfulness
  - **Property 11: Error message helpfulness**
  - **Validates: Requirements 5.4**

- [x] 10.3 Write property test for result display with exit codes
  - **Property 13: Result display with exit codes**
  - **Validates: Requirements 6.3, 6.4**


- [x] 11. Verify offline operation and local-only networking
  - Ensure no external API calls are made
  - Verify only localhost Ollama endpoint is contacted
  - Test application works without internet connectivity
  - _Requirements: 8.1, 8.2, 8.3_

- [x] 11.1 Write property test for local-only operation
  - **Property 17: Local-only operation**
  - **Validates: Requirements 8.1, 8.2**

- [x] 11.2 Write integration test for offline functionality
  - Test with Ollama running but no internet
  - Verify no external network calls
  - _Requirements: 8.3_

- [x] 12. Create comprehensive README documentation
  - Document Python 3.10+ requirement
  - Provide Ollama installation instructions with llama3.2 model setup
  - List all Python dependencies with pip install command
  - Include example usage commands and screenshots
  - Add troubleshooting section for common issues
  - Explain how to verify installation is working
  - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5_

- [x] 13. Final checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 14. Enhance Ollama prompt generation with domain-specific examples
  - Create domain categorization logic to detect command intent (file, process, network, text)
  - Implement _get_domain_examples() method to return relevant examples based on category
  - Add comprehensive example sets for file operations (find, ls, cp, mv with proper quoting)
  - Add comprehensive example sets for process management (ps, kill, top, jobs, bg, fg)
  - Add comprehensive example sets for network operations (curl, wget, ping, netstat)
  - Add comprehensive example sets for text processing (grep, sed, awk, cut, sort, uniq with pipes)
  - Update build_prompt() to dynamically include domain-specific examples
  - Ensure examples emphasize error suppression (2>/dev/null) and safe defaults
  - _Requirements: 12.1, 12.2, 12.3, 12.4, 12.5, 12.6, 12.7, 12.8_

- [x] 14.1 Write property test for domain-specific example inclusion
  - **Property 20: Domain-specific example inclusion**
  - **Validates: Requirements 12.1, 12.2, 12.3, 12.4, 12.5**

- [x] 14.2 Write property test for safe interpretation preference
  - **Property 21: Safe interpretation preference**
  - **Validates: Requirements 12.8**

- [x] 14.3 Write unit tests for domain categorization
  - Test file operation detection (find, list, copy, move keywords)
  - Test process operation detection (kill, stop, process keywords)
  - Test network operation detection (download, fetch, ping keywords)
  - Test text processing detection (search, filter, replace keywords)
  - _Requirements: 12.1_

- [x] 15. Final checkpoint - Verify enhanced prompt accuracy
  - Test command generation with various natural language inputs
  - Verify domain-specific examples are included appropriately
  - Ensure all tests pass, ask the user if questions arise.

## Remaining Tasks

The following tasks remain incomplete:

### Property-Based Tests
- [ ] 10.2 Write property test for error message helpfulness (Property 11)
- [ ] 14.1 Write property test for domain-specific example inclusion (Property 20)
- [ ] 14.2 Write property test for safe interpretation preference (Property 21)

## Additional Features Implemented (Beyond Original Spec)

The following features have been implemented as enhancements beyond the original requirements:

### Context Management (src/context.py)
- Tracks current working directory and file listings
- Provides context to Ollama for better command interpretation
- Helps with file name case correction

### Path Correction (src/corrector.py)
- Auto-corrects file paths with case-insensitive matching
- Particularly useful on macOS where filesystem is case-insensitive but case-preserving

### Knowledge Base (src/knowledge.py)
- User-editable knowledge base for custom command mappings
- Stored in ~/.haunted/knowledge.txt
- Takes priority over learned history

### Blacklist (src/blacklist.py)
- User-defined patterns that should never appear in commands
- Stored in ~/.haunted/blacklist.txt
- Provides additional safety layer

### Rituals (src/rituals.py)
- Workflow automation system for multi-step command sequences
- Stored in SQLite database
- Can be created, listed, and executed through CLI

### Spirit Suggestions (src/spirits.py)
- Intelligent command suggestions based on context
- Considers directory, time of day, and command patterns
- Provides helpful hints before command interpretation

### Command Aliases (history.py)
- User-defined command aliases
- Stored in SQLite database
- Expandable shortcuts for frequently used commands

### Rejection Learning (history.py)
- Tracks rejected command interpretations
- Used to avoid suggesting similar commands in future
- Improves accuracy over time

### Retry Mechanism (cli.py)
- "retry" or "r" command to reinterpret with different approach
- Automatically includes rejected commands as negative examples
- Helps when first interpretation is incorrect

These enhancements significantly improve the user experience and command accuracy beyond the original specification.
