# Domain-Specific Examples Implementation

## Overview

Enhanced the Ollama client to dynamically include domain-specific examples in prompts based on the user's natural language input. This improves command interpretation accuracy by providing relevant examples for the detected command category.

## Implementation Details

### 1. Domain Categorization (`_categorize_domain`)

Analyzes user input to detect command intent across four domains:

- **File Operations**: find, search, list, copy, move, delete, disk operations
- **Process Management**: kill, stop, ps, top, jobs, background/foreground
- **Network Operations**: download, curl, wget, ping, netstat, API requests
- **Text Processing**: grep, sed, awk, sort, uniq, pipes, pattern matching

The method returns a list of detected domains, allowing for multi-domain detection (e.g., "search for python files and count lines" detects both 'file' and 'text').

### 2. Domain-Specific Examples (`_get_domain_examples`)

Generates relevant examples based on detected domains:

#### File Operations Examples
- Finding files with proper quoting and wildcards
- Copying and moving with error suppression
- Directory size operations
- All examples include `2>/dev/null` for error suppression

#### Process Management Examples
- Listing processes with `ps aux`
- Killing processes
- Top CPU consumers
- Background/foreground job management

#### Network Operations Examples
- Downloading with curl and wget
- API requests
- Ping and connectivity testing
- Port checking with netstat

#### Text Processing Examples
- Grep patterns with proper flags
- Sed replacements (macOS-compatible with `sed -i ''`)
- Pipe combinations
- Sorting and uniqueness operations
- Line and word counting

### 3. Enhanced Prompt Building

The `build_prompt` method now:
1. Analyzes user input to detect domains
2. Dynamically includes relevant examples
3. Maintains backward compatibility with history, rejections, and blacklist features
4. Emphasizes safe defaults and error suppression throughout

## Key Features

### Error Suppression
All file and search operations include `2>/dev/null` to suppress permission errors, making commands more user-friendly.

### Proper Quoting
Examples demonstrate proper quoting for filenames with spaces and special characters.

### Safe Defaults
When ambiguous, examples favor non-destructive operations and include appropriate error handling.

### macOS Compatibility
- Uses `sed -i ''` syntax for in-place editing
- Includes macOS-specific commands where appropriate

### Pipe Combinations
Text processing examples show proper use of pipes for complex operations.

## Testing

All existing tests pass, including:
- 19 unit tests for Ollama client functionality
- Property-based test for request formation
- Integration with offline operation tests

## Requirements Validated

This implementation satisfies:
- **Requirement 12.1**: Domain-specific examples for common command categories
- **Requirement 12.2**: File operation examples with proper quoting and path handling
- **Requirement 12.3**: Process management examples
- **Requirement 12.4**: Network operation examples
- **Requirement 12.5**: Text processing examples with pipes
- **Requirement 12.6**: Platform-specific guidance (macOS)
- **Requirement 12.7**: Proper shell operators (pipes, redirects, chaining)
- **Requirement 12.8**: Safe, non-destructive interpretations with error suppression

## Example Output

For input "find all python files":
```
File Operations:
User: "list all python files"
Response: find . -name "*.py" 2>/dev/null

User: "find all pdf files in my home directory"
Response: find ~ -name "*.pdf" 2>/dev/null

User: "find files larger than 100MB"
Response: find . -type f -size +100M 2>/dev/null
...
```

For input "kill process 1234":
```
Process Management:
User: "show all running processes"
Response: ps aux

User: "find python processes"
Response: ps aux | grep python

User: "kill process 1234"
Response: kill 1234
...
```

## Impact

This enhancement significantly improves the quality of command interpretations by:
1. Providing context-relevant examples to the LLM
2. Demonstrating best practices (error suppression, quoting, safe defaults)
3. Reducing the need for user corrections and rejections
4. Improving first-try accuracy for common operations
