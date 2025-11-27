# Requirements Document

## Introduction

The Haunted Terminal CLI is a Python-based command-line application that interprets natural language commands using a local LLM (Ollama with llama3.2) and executes real system commands with a spooky Halloween-themed interface. The application operates completely offline after initial setup, prioritizes user safety through confirmation prompts for destructive operations, and provides an engaging themed experience with purple, orange, and green color schemes.

## Glossary

- **Haunted Terminal**: The Python CLI application system
- **Ollama**: Local LLM service running llama3.2 model
- **Natural Language Command**: User input in plain English describing desired system operation
- **Shell Command**: Actual system command to be executed (bash/zsh)
- **Destructive Operation**: Commands that modify or delete files (rm, mv, dd, format, etc.)
- **Spooky Theme**: Halloween aesthetic using gothic borders, mystical symbols, and themed colors
- **User**: Person interacting with the Haunted Terminal CLI

## Requirements

### Requirement 1

**User Story:** As a user, I want to input natural language commands in the terminal, so that I can interact with my system without memorizing exact command syntax.

#### Acceptance Criteria

1. WHEN the Haunted Terminal starts THEN the system SHALL display a themed prompt accepting text input
2. WHEN a user enters natural language text THEN the Haunted Terminal SHALL accept input of any length up to 1000 characters
3. WHEN a user submits empty input THEN the Haunted Terminal SHALL display a themed message and re-prompt for input
4. WHEN a user types "exit" or "quit" THEN the Haunted Terminal SHALL terminate gracefully with a themed farewell message
5. WHEN the Haunted Terminal is running THEN the system SHALL maintain a command history for the session


### Requirement 2

**User Story:** As a user, I want Ollama to interpret my natural language into shell commands, so that I can execute system operations using plain English.

#### Acceptance Criteria

1. WHEN a user submits natural language input THEN the Haunted Terminal SHALL send the input to Ollama running locally
2. WHEN Ollama processes the input THEN the system SHALL receive a shell command interpretation within 10 seconds
3. WHEN Ollama cannot interpret the input THEN the Haunted Terminal SHALL display a themed error message and re-prompt
4. WHEN the Ollama service is unavailable THEN the Haunted Terminal SHALL display a connection error with troubleshooting guidance
5. WHEN Ollama returns a command THEN the system SHALL validate the command syntax before presenting to the user

### Requirement 3

**User Story:** As a user, I want to see what command will be executed before it runs, so that I can verify the interpretation is correct.

#### Acceptance Criteria

1. WHEN Ollama interprets a command THEN the Haunted Terminal SHALL display the shell command with themed formatting
2. WHEN displaying the command THEN the system SHALL show both the original natural language and the interpreted shell command
3. WHEN a command is displayed THEN the Haunted Terminal SHALL prompt the user for confirmation before execution
4. WHEN a user confirms execution THEN the system SHALL proceed to run the command
5. WHEN a user rejects execution THEN the Haunted Terminal SHALL cancel the operation and return to the input prompt

### Requirement 4

**User Story:** As a user, I want protection from destructive operations, so that I don't accidentally damage my system.

#### Acceptance Criteria

1. WHEN Ollama interprets a destructive command THEN the Haunted Terminal SHALL identify it as destructive based on command patterns
2. WHEN a destructive command is identified THEN the system SHALL display a prominent warning with themed styling
3. WHEN prompting for destructive operations THEN the Haunted Terminal SHALL require explicit typed confirmation beyond simple yes/no
4. WHEN a user cancels a destructive operation THEN the system SHALL log the cancelled command and return safely to prompt
5. IF a command contains patterns matching rm, mv, dd, format, or mkfs THEN the Haunted Terminal SHALL classify it as destructive


### Requirement 5

**User Story:** As a user, I want to see command execution results with a spooky theme, so that the experience is engaging and visually distinctive.

#### Acceptance Criteria

1. WHEN displaying any output THEN the Haunted Terminal SHALL use purple, orange, and green color schemes
2. WHEN showing command results THEN the system SHALL frame output with gothic borders and mystical symbols
3. WHEN a command succeeds THEN the Haunted Terminal SHALL display success messages with magical themed language
4. WHEN a command fails THEN the system SHALL display error messages that are spooky but helpful
5. WHEN rendering text THEN the Haunted Terminal SHALL use the rich library for terminal styling

### Requirement 6

**User Story:** As a user, I want the application to execute real shell commands, so that I can perform actual system operations.

#### Acceptance Criteria

1. WHEN a user confirms a command THEN the Haunted Terminal SHALL execute it using subprocess with shell=True
2. WHEN a command executes THEN the system SHALL capture both stdout and stderr streams
3. WHEN a command completes THEN the Haunted Terminal SHALL display the output with themed formatting
4. WHEN a command returns a non-zero exit code THEN the system SHALL display the error with exit code information
5. WHEN executing commands THEN the Haunted Terminal SHALL preserve the user's current working directory context

### Requirement 7

**User Story:** As a user, I want graceful error handling, so that problems don't crash the application.

#### Acceptance Criteria

1. WHEN any exception occurs THEN the Haunted Terminal SHALL catch it and display a themed error message
2. WHEN Ollama connection fails THEN the system SHALL provide specific troubleshooting steps
3. WHEN a command execution fails THEN the Haunted Terminal SHALL display stderr output with helpful context
4. WHEN an unexpected error occurs THEN the system SHALL log the error details and continue running
5. WHEN recovering from errors THEN the Haunted Terminal SHALL return to the main input prompt


### Requirement 8

**User Story:** As a user, I want the application to work completely offline, so that I maintain privacy and don't depend on internet connectivity.

#### Acceptance Criteria

1. WHEN the Haunted Terminal runs THEN the system SHALL use only local Ollama service without external API calls
2. WHEN processing commands THEN the system SHALL not transmit any data over the network
3. WHEN Ollama is properly installed THEN the Haunted Terminal SHALL function without internet connectivity
4. WHEN checking dependencies THEN the system SHALL verify Ollama is available locally before starting
5. WHEN the application starts THEN the Haunted Terminal SHALL display a message confirming offline operation mode

### Requirement 9

**User Story:** As a developer, I want clear setup instructions, so that I can install and run the application easily.

#### Acceptance Criteria

1. WHEN the README is provided THEN the system documentation SHALL include Python version requirements (3.10+)
2. WHEN the README is provided THEN the documentation SHALL include Ollama installation instructions
3. WHEN the README is provided THEN the documentation SHALL list all Python dependencies with installation commands
4. WHEN the README is provided THEN the documentation SHALL include example usage commands
5. WHEN the README is provided THEN the documentation SHALL explain how to verify the installation is working

### Requirement 10

**User Story:** As a user, I want to launch the application with a simple command, so that I can start using it quickly.

#### Acceptance Criteria

1. WHEN the application is installed THEN the user SHALL be able to launch it with "python haunted.py"
2. WHEN the application starts THEN the Haunted Terminal SHALL display a themed welcome banner
3. WHEN starting up THEN the system SHALL verify all dependencies are available
4. WHEN dependencies are missing THEN the Haunted Terminal SHALL display specific installation instructions
5. WHEN the application is ready THEN the system SHALL display the main input prompt


### Requirement 11

**User Story:** As a user, I want the CLI to remember my command patterns across sessions, so that it can suggest relevant commands based on my history.

#### Acceptance Criteria

1. WHEN a command executes successfully THEN the Haunted Terminal SHALL persist the command to a local SQLite database
2. WHEN storing command history THEN the system SHALL record the natural language input, shell command, timestamp, and working directory
3. WHEN a user enters natural language similar to past commands THEN the Haunted Terminal SHALL retrieve and suggest matching historical commands
4. WHEN displaying suggestions THEN the system SHALL show the most recent and frequently used commands with themed formatting
5. WHEN the application starts THEN the Haunted Terminal SHALL initialize the SQLite database if it does not exist

### Requirement 12

**User Story:** As a user, I want Ollama to generate more accurate shell commands through enhanced prompts, so that I get better interpretations on the first try.

#### Acceptance Criteria

1. WHEN building prompts THEN the system SHALL include domain-specific examples for common command categories (file operations, process management, network operations, text processing)
2. WHEN interpreting file-related commands THEN the system SHALL provide examples that demonstrate proper quoting, path handling, and wildcard usage
3. WHEN interpreting process-related commands THEN the system SHALL include examples for ps, kill, top, and background job management
4. WHEN interpreting network-related commands THEN the system SHALL include examples for curl, wget, netstat, and connectivity testing
5. WHEN interpreting text-processing commands THEN the system SHALL include examples for grep, sed, awk, and pipe combinations
6. WHEN building prompts THEN the system SHALL include platform-specific guidance for macOS-specific commands and behaviors
7. WHEN the user request involves multiple operations THEN the system SHALL generate commands using proper shell operators (pipes, redirects, command chaining)
8. WHEN ambiguous requests are detected THEN the system SHALL favor safe, non-destructive interpretations with appropriate error suppression
