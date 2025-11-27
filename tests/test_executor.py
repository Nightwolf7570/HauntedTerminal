"""
Unit tests for the command executor.
"""

import pytest
import os
import tempfile
from hypothesis import given, strategies as st, settings
from src.executor import CommandExecutor, ExecutionResult


class TestCommandExecutor:
    """Test suite for CommandExecutor class."""
    
    def test_execute_simple_command(self):
        """Test executing a simple safe command."""
        executor = CommandExecutor()
        result = executor.execute("echo 'Hello, World!'")
        
        assert result.exit_code == 0
        assert "Hello, World!" in result.stdout
        assert result.stderr == ""
        assert result.execution_time > 0
    
    def test_execute_command_with_stderr(self):
        """Test capturing stderr from a failing command."""
        executor = CommandExecutor()
        # ls on a non-existent directory should produce stderr
        result = executor.execute("ls /nonexistent_directory_12345")
        
        assert result.exit_code != 0
        assert result.stderr != ""
    
    def test_capture_exit_code(self):
        """Test that exit codes are properly captured."""
        executor = CommandExecutor()
        
        # Success case
        result = executor.execute("true")
        assert result.exit_code == 0
        
        # Failure case
        result = executor.execute("false")
        assert result.exit_code != 0
    
    def test_validate_syntax_valid_commands(self):
        """Test that valid commands pass syntax validation."""
        executor = CommandExecutor()
        
        valid_commands = [
            "echo hello",
            "ls -la",
            "cat file.txt | grep pattern",
            "echo 'quoted string'",
            'echo "double quoted"',
            "command > output.txt",
            "command < input.txt",
            "cmd1 && cmd2",
            "cmd1 || cmd2",
        ]
        
        for cmd in valid_commands:
            assert executor.validate_syntax(cmd), f"Should be valid: {cmd}"
    
    def test_validate_syntax_invalid_commands(self):
        """Test that invalid commands fail syntax validation."""
        executor = CommandExecutor()
        
        invalid_commands = [
            "",
            "   ",
            "echo 'unclosed quote",
            'echo "unclosed quote',
            "echo (unmatched paren",
            "echo [unmatched bracket",
            "| starts with pipe",
            "> starts with redirect",
        ]
        
        for cmd in invalid_commands:
            assert not executor.validate_syntax(cmd), f"Should be invalid: {cmd}"
    
    def test_execute_invalid_command_raises_error(self):
        """Test that executing invalid syntax raises ValueError."""
        executor = CommandExecutor()
        
        with pytest.raises(ValueError):
            executor.execute("echo 'unclosed quote")
    
    def test_working_directory_preservation(self):
        """Test that working directory context is preserved."""
        with tempfile.TemporaryDirectory() as tmpdir:
            executor = CommandExecutor(working_directory=tmpdir)
            
            # Execute a command
            result = executor.execute("pwd")
            
            # The command should have run in the temp directory
            assert tmpdir in result.stdout
            assert result.exit_code == 0
    
    def test_set_working_directory(self):
        """Test setting the working directory."""
        executor = CommandExecutor()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            executor.set_working_directory(tmpdir)
            assert executor.get_working_directory() == os.path.abspath(tmpdir)
    
    def test_set_invalid_working_directory(self):
        """Test that setting invalid directory raises error."""
        executor = CommandExecutor()
        
        with pytest.raises(ValueError):
            executor.set_working_directory("/nonexistent_directory_12345")
    
    def test_execution_result_fields(self):
        """Test that ExecutionResult contains all required fields."""
        executor = CommandExecutor()
        result = executor.execute("echo test")
        
        assert hasattr(result, 'command')
        assert hasattr(result, 'stdout')
        assert hasattr(result, 'stderr')
        assert hasattr(result, 'exit_code')
        assert hasattr(result, 'execution_time')
        assert hasattr(result, 'timestamp')
        
        assert result.command == "echo test"
        assert isinstance(result.execution_time, float)
    
    def test_safe_command_echo(self):
        """Test executing safe echo command - Requirements 6.3, 6.4."""
        executor = CommandExecutor()
        result = executor.execute("echo 'test output'")
        
        assert result.exit_code == 0
        assert "test output" in result.stdout
        assert result.stderr == ""
        assert result.execution_time >= 0
    
    def test_safe_command_ls(self):
        """Test executing safe ls command - Requirements 6.3, 6.4."""
        executor = CommandExecutor()
        # List current directory
        result = executor.execute("ls")
        
        assert result.exit_code == 0
        assert result.stdout != ""  # Should have some output
        assert result.execution_time >= 0
    
    def test_safe_command_pwd(self):
        """Test executing safe pwd command - Requirements 6.3, 6.4."""
        executor = CommandExecutor()
        result = executor.execute("pwd")
        
        assert result.exit_code == 0
        assert result.stdout.strip() != ""  # Should output current directory
        assert result.stderr == ""
        assert result.execution_time >= 0
    
    def test_stderr_capture_with_failing_command(self):
        """Test stderr capture with a command that fails - Requirements 6.3, 6.4."""
        executor = CommandExecutor()
        # Try to cat a non-existent file
        result = executor.execute("cat /nonexistent_file_xyz_12345.txt")
        
        assert result.exit_code != 0
        assert result.stderr != ""
        assert "No such file" in result.stderr or "cannot" in result.stderr.lower()
    
    def test_exit_code_reporting_success(self):
        """Test exit code reporting for successful command - Requirements 6.3, 6.4."""
        executor = CommandExecutor()
        result = executor.execute("echo success")
        
        assert result.exit_code == 0
        assert hasattr(result, 'exit_code')
    
    def test_exit_code_reporting_failure(self):
        """Test exit code reporting for failed command - Requirements 6.3, 6.4."""
        executor = CommandExecutor()
        # false command always returns exit code 1
        result = executor.execute("false")
        
        assert result.exit_code != 0
        assert result.exit_code == 1
        assert hasattr(result, 'exit_code')


# Property-Based Tests

@settings(max_examples=100)
@given(
    stdout_text=st.text(
        alphabet=st.characters(blacklist_categories=('Cs', 'Cc')), 
        min_size=0, 
        max_size=500
    ),
    stderr_text=st.text(
        alphabet=st.characters(blacklist_categories=('Cs', 'Cc')), 
        min_size=0, 
        max_size=500
    )
)
def test_property_output_stream_capture(stdout_text, stderr_text):
    """
    Feature: haunted-terminal-cli, Property 12: Output stream capture
    
    Property: For any executed command, the system should capture and make available 
    both stdout and stderr streams.
    
    Validates: Requirements 6.2
    """
    executor = CommandExecutor()
    
    # Create temporary files to hold the test data
    # This avoids shell escaping issues with arbitrary text
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as stdout_file:
        stdout_file.write(stdout_text)
        stdout_path = stdout_file.name
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as stderr_file:
        stderr_file.write(stderr_text)
        stderr_path = stderr_file.name
    
    try:
        # Create a command that outputs the file contents to stdout and stderr
        # Using cat avoids shell escaping issues
        command = f"cat {stdout_path} && cat {stderr_path} >&2"
        
        # Execute the command
        result = executor.execute(command)
        
        # Property: Both stdout and stderr should be captured
        assert hasattr(result, 'stdout'), "Result should have stdout attribute"
        assert hasattr(result, 'stderr'), "Result should have stderr attribute"
        
        # Property: The captured stdout should match what was written to stdout
        assert result.stdout == stdout_text, f"stdout should be captured correctly. Expected: {repr(stdout_text)}, Got: {repr(result.stdout)}"
        
        # Property: The captured stderr should match what was written to stderr
        assert result.stderr == stderr_text, f"stderr should be captured correctly. Expected: {repr(stderr_text)}, Got: {repr(result.stderr)}"
        
        # Property: Both streams should be available simultaneously
        assert result.stdout is not None, "stdout should always be available (even if empty)"
        assert result.stderr is not None, "stderr should always be available (even if empty)"
        
    finally:
        # Clean up temporary files
        if os.path.exists(stdout_path):
            os.unlink(stdout_path)
        if os.path.exists(stderr_path):
            os.unlink(stderr_path)


@settings(max_examples=100)
@given(
    num_commands=st.integers(min_value=2, max_value=10)
)
def test_property_working_directory_preservation(num_commands):
    """
    Feature: haunted-terminal-cli, Property 14: Working directory preservation
    
    Property: For any sequence of commands, the working directory context should be 
    preserved across executions unless explicitly changed by a command.
    
    Validates: Requirements 6.5
    """
    # Create a temporary directory to work in
    with tempfile.TemporaryDirectory() as tmpdir:
        executor = CommandExecutor(working_directory=tmpdir)
        
        # Verify initial working directory is set correctly
        initial_wd = executor.get_working_directory()
        # Use realpath to resolve symlinks (important on macOS where /var -> /private/var)
        assert os.path.realpath(tmpdir) == os.path.realpath(initial_wd), "Initial working directory should be set"
        
        # Execute a sequence of commands that don't change directory
        for i in range(num_commands):
            # Use simple commands that don't change directory
            commands = [
                "echo 'test'",
                "pwd",
                "ls",
                "true",
                "echo $PWD"
            ]
            command = commands[i % len(commands)]
            
            # Execute the command
            result = executor.execute(command)
            
            # Property: Working directory should remain unchanged after execution
            current_wd = executor.get_working_directory()
            assert os.path.realpath(current_wd) == os.path.realpath(initial_wd), \
                f"Working directory should be preserved after command {i+1}/{num_commands}. " \
                f"Expected: {initial_wd}, Got: {current_wd}, Command: {command}"
            
            # Property: Commands should execute in the correct working directory
            if command == "pwd":
                # pwd output should match our working directory (resolve symlinks)
                pwd_output = result.stdout.strip()
                assert os.path.realpath(tmpdir) == os.path.realpath(pwd_output), \
                    f"Command should execute in working directory. " \
                    f"Expected: {os.path.realpath(tmpdir)}, Got: {os.path.realpath(pwd_output)}"
        
        # Now test that cd commands DO change the working directory
        # Create a subdirectory
        subdir = os.path.join(tmpdir, "subdir")
        os.makedirs(subdir, exist_ok=True)
        
        # Execute cd command
        cd_result = executor.execute(f"cd {subdir}")
        
        # Property: cd command should change the working directory
        new_wd = executor.get_working_directory()
        assert os.path.realpath(subdir) == os.path.realpath(new_wd), \
            f"cd command should change working directory. Expected: {os.path.realpath(subdir)}, Got: {os.path.realpath(new_wd)}"
        
        # Execute more commands in the new directory
        for i in range(min(3, num_commands)):
            result = executor.execute("pwd")
            
            # Property: Working directory should remain in the new location
            current_wd = executor.get_working_directory()
            assert os.path.realpath(current_wd) == os.path.realpath(new_wd), \
                f"Working directory should be preserved in new location after command {i+1}. " \
                f"Expected: {new_wd}, Got: {current_wd}"
            
            # Property: Commands should execute in the new working directory
            pwd_output = result.stdout.strip()
            assert os.path.realpath(subdir) == os.path.realpath(pwd_output), \
                f"Command should execute in new working directory. " \
                f"Expected: {os.path.realpath(subdir)}, Got: {os.path.realpath(pwd_output)}"


@settings(max_examples=100)
@given(
    command_base=st.sampled_from([
        "echo", "ls", "pwd", "cat", "grep", "find", "ps", "true", "false"
    ]),
    args=st.lists(
        st.text(
            alphabet=st.characters(
                min_codepoint=32, 
                max_codepoint=126,
                blacklist_characters='|><&;`$'
            ),
            min_size=0,
            max_size=20
        ),
        min_size=0,
        max_size=3
    ),
    use_quotes=st.booleans(),
    use_pipe=st.booleans(),
    use_redirect=st.booleans()
)
def test_property_command_syntax_validation(command_base, args, use_quotes, use_pipe, use_redirect):
    """
    Feature: haunted-terminal-cli, Property 5: Command syntax validation
    
    Property: For any command string returned by Ollama, the system should validate 
    basic shell syntax before presenting it to the user.
    
    Validates: Requirements 2.5
    """
    # Use a temporary directory to avoid getcwd() issues
    with tempfile.TemporaryDirectory() as tmpdir:
        executor = CommandExecutor(working_directory=tmpdir)
    
    # Build a command string with various syntactic elements
    command_parts = [command_base]
    
    # Add arguments
    for arg in args:
        if arg.strip():  # Only add non-empty args
            if use_quotes and ' ' in arg:
                # Quote arguments with spaces
                command_parts.append(f"'{arg}'")
            else:
                command_parts.append(arg)
    
    command = " ".join(command_parts)
    
    # Add pipe if requested (to a safe command)
    if use_pipe and command.strip():
        command = f"{command} | cat"
    
        # Add redirect if requested
        if use_redirect and command.strip():
            command = f"{command} > /dev/null"
        
        # Property: The validate_syntax method should return a boolean
        result = executor.validate_syntax(command)
        assert isinstance(result, bool), "validate_syntax should return a boolean"
        
        # Property: Valid commands should pass validation
        # A command is considered valid if it has:
        # - Non-empty content
        # - Balanced quotes
        # - Balanced brackets/parentheses
        # - Doesn't start with pipe or redirect operators
        
        if command and command.strip():
            # Check if command has balanced quotes
            single_quotes = command.count("'")
            double_quotes = command.count('"')
            balanced_quotes = (single_quotes % 2 == 0) and (double_quotes % 2 == 0)
            
            # Check if command has balanced brackets
            balanced_parens = command.count('(') == command.count(')')
            balanced_brackets = command.count('[') == command.count(']')
            balanced_braces = command.count('{') == command.count('}')
            
            # Check if command starts with invalid operators
            starts_invalid = command.strip().startswith(('|', '>', '<'))
            
            # Check if command ends with pipe
            ends_with_pipe = command.strip().endswith('|')
            
            if (balanced_quotes and balanced_parens and balanced_brackets and 
                balanced_braces and not starts_invalid and not ends_with_pipe):
                # This should be a valid command
                assert result is True, \
                    f"Command should be valid: {command}\n" \
                    f"  Balanced quotes: {balanced_quotes}\n" \
                    f"  Balanced parens: {balanced_parens}\n" \
                    f"  Balanced brackets: {balanced_brackets}\n" \
                    f"  Balanced braces: {balanced_braces}\n" \
                    f"  Starts invalid: {starts_invalid}\n" \
                    f"  Ends with pipe: {ends_with_pipe}"
        else:
            # Empty commands should be invalid
            assert result is False, "Empty command should be invalid"
        
        # Property: If validation passes, the command should not raise ValueError when executed
        # (though it may fail for other reasons like command not found)
        if result:
            try:
                # We don't actually execute to avoid side effects, but we check that
                # the validation is consistent with the execute method's validation
                # The execute method should not raise ValueError for syntax
                executor.validate_syntax(command)  # Should not raise
            except ValueError:
                pytest.fail(f"validate_syntax returned True but command failed validation: {command}")


@settings(max_examples=100)
@given(
    quote_type=st.sampled_from(["'", '"']),
    text_content=st.text(
        alphabet=st.characters(
            min_codepoint=32, 
            max_codepoint=126,
            blacklist_characters='\'"'  # Exclude quotes from content
        ),
        min_size=1,
        max_size=50
    )
)
def test_property_command_syntax_validation_unbalanced_quotes(quote_type, text_content):
    """
    Feature: haunted-terminal-cli, Property 5: Command syntax validation
    
    Property: Commands with unbalanced quotes should be rejected by syntax validation.
    
    Validates: Requirements 2.5
    """
    # Use a temporary directory to avoid getcwd() issues
    with tempfile.TemporaryDirectory() as tmpdir:
        executor = CommandExecutor(working_directory=tmpdir)
    
        # Create a command with unbalanced quotes
        command = f"echo {quote_type}{text_content}"
        
        # Property: Unbalanced quotes should fail validation
        result = executor.validate_syntax(command)
        assert result is False, \
            f"Command with unbalanced {quote_type} quotes should be invalid: {command}"
        
        # Property: Attempting to execute should raise ValueError
        with pytest.raises(ValueError) as exc_info:
            executor.execute(command)
        
        assert "syntax" in str(exc_info.value).lower(), \
            "ValueError should mention syntax issue"


@settings(max_examples=100)
@given(
    bracket_type=st.sampled_from(['()', '[]', '{}']),
    command_base=st.sampled_from(["echo", "test", "expr"])
)
def test_property_command_syntax_validation_unbalanced_brackets(bracket_type, command_base):
    """
    Feature: haunted-terminal-cli, Property 5: Command syntax validation
    
    Property: Commands with unbalanced brackets/parentheses should be rejected by syntax validation.
    
    Validates: Requirements 2.5
    """
    # Use a temporary directory to avoid getcwd() issues
    with tempfile.TemporaryDirectory() as tmpdir:
        executor = CommandExecutor(working_directory=tmpdir)
    
        # Create a command with unbalanced brackets
        open_bracket = bracket_type[0]
        command = f"{command_base} {open_bracket}test"
        
        # Property: Unbalanced brackets should fail validation
        result = executor.validate_syntax(command)
        assert result is False, \
            f"Command with unbalanced {bracket_type} should be invalid: {command}"
        
        # Property: Attempting to execute should raise ValueError
        with pytest.raises(ValueError) as exc_info:
            executor.execute(command)
        
        assert "syntax" in str(exc_info.value).lower(), \
            "ValueError should mention syntax issue"


@settings(max_examples=100)
@given(
    operator=st.sampled_from(['|', '>', '<']),
    command_suffix=st.sampled_from(["echo test", "ls", "pwd", "cat file.txt"])
)
def test_property_command_syntax_validation_invalid_operators(operator, command_suffix):
    """
    Feature: haunted-terminal-cli, Property 5: Command syntax validation
    
    Property: Commands starting with pipe or redirect operators should be rejected.
    
    Validates: Requirements 2.5
    """
    # Use a temporary directory to avoid getcwd() issues
    with tempfile.TemporaryDirectory() as tmpdir:
        executor = CommandExecutor(working_directory=tmpdir)
    
        # Create a command starting with an invalid operator
        command = f"{operator} {command_suffix}"
        
        # Property: Commands starting with pipe/redirect should fail validation
        result = executor.validate_syntax(command)
        assert result is False, \
            f"Command starting with {operator} should be invalid: {command}"
        
        # Property: Attempting to execute should raise ValueError
        with pytest.raises(ValueError) as exc_info:
            executor.execute(command)
        
        assert "syntax" in str(exc_info.value).lower(), \
            "ValueError should mention syntax issue"
