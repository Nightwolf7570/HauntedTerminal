"""
Tests for CLI interface.
"""

import pytest
import sqlite3
from unittest.mock import Mock, patch, MagicMock
from hypothesis import given, strategies as st, settings
from src.cli import HauntedCLI, SessionCommand
from src.executor import ExecutionResult
from datetime import datetime


class TestHauntedCLI:
    """Test suite for HauntedCLI class."""
    
    def test_initialization(self):
        """Test CLI initializes with default components."""
        cli = HauntedCLI()
        
        assert cli.theme is not None
        assert cli.ollama is not None
        assert cli.executor is not None
        assert cli.history is not None
        assert cli.session_history == []
        assert cli.running is False
    
    def test_initialization_with_custom_components(self):
        """Test CLI accepts custom components."""
        mock_theme = Mock()
        mock_ollama = Mock()
        mock_executor = Mock()
        mock_history = Mock()
        
        cli = HauntedCLI(
            theme=mock_theme,
            ollama=mock_ollama,
            executor=mock_executor,
            history=mock_history
        )
        
        assert cli.theme is mock_theme
        assert cli.ollama is mock_ollama
        assert cli.executor is mock_executor
        assert cli.history is mock_history
    
    def test_get_user_input_valid(self):
        """Test getting valid user input."""
        cli = HauntedCLI()
        
        with patch('builtins.input', return_value='list files'):
            result = cli.get_user_input()
            assert result == 'list files'
    
    def test_get_user_input_exit_command(self):
        """Test exit commands return None."""
        cli = HauntedCLI()
        
        with patch('builtins.input', return_value='exit'):
            result = cli.get_user_input()
            assert result is None
        
        with patch('builtins.input', return_value='quit'):
            result = cli.get_user_input()
            assert result is None
    
    def test_get_user_input_empty(self):
        """Test empty input returns empty string."""
        cli = HauntedCLI()
        
        with patch('builtins.input', return_value=''):
            result = cli.get_user_input()
            assert result == ''
        
        with patch('builtins.input', return_value='   '):
            result = cli.get_user_input()
            assert result == ''
    
    def test_get_user_input_too_long(self):
        """Test input over 1000 characters is rejected."""
        cli = HauntedCLI()
        long_input = 'a' * 1001
        
        with patch('builtins.input', return_value=long_input):
            result = cli.get_user_input()
            assert result == ''
    
    def test_get_user_input_keyboard_interrupt(self):
        """Test Ctrl+C returns None."""
        cli = HauntedCLI()
        
        with patch('builtins.input', side_effect=KeyboardInterrupt):
            result = cli.get_user_input()
            assert result is None
    
    def test_display_command_preview(self):
        """Test command preview display."""
        cli = HauntedCLI()
        
        # Should not raise any exceptions
        cli.display_command_preview("list files", "ls -la")
    
    def test_display_output_success(self):
        """Test displaying successful command output."""
        cli = HauntedCLI()
        
        result = ExecutionResult(
            command="echo test",
            stdout="test\n",
            stderr="",
            exit_code=0,
            execution_time=0.1,
            timestamp=datetime.now()
        )
        
        # Should not raise any exceptions
        cli.display_output(result)
    
    def test_display_output_failure(self):
        """Test displaying failed command output."""
        cli = HauntedCLI()
        
        result = ExecutionResult(
            command="false",
            stdout="",
            stderr="command failed",
            exit_code=1,
            execution_time=0.05,
            timestamp=datetime.now()
        )
        
        # Should not raise any exceptions
        cli.display_output(result)
    
    def test_get_session_history(self):
        """Test retrieving session history."""
        cli = HauntedCLI()
        
        # Add some commands to session history
        cmd1 = SessionCommand(
            natural_language="list files",
            shell_command="ls",
            result=None
        )
        cmd2 = SessionCommand(
            natural_language="show date",
            shell_command="date",
            result=None
        )
        
        cli.session_history.append(cmd1)
        cli.session_history.append(cmd2)
        
        history = cli.get_session_history()
        
        assert len(history) == 2
        assert history[0].natural_language == "list files"
        assert history[1].natural_language == "show date"
        
        # Verify it's a copy, not the original
        assert history is not cli.session_history
    
    def test_display_welcome(self):
        """Test welcome banner display."""
        cli = HauntedCLI()
        
        # Should not raise any exceptions
        cli.display_welcome()
    
    def test_session_history_maintains_order(self):
        """Test that session history maintains chronological order."""
        cli = HauntedCLI()
        
        commands = [
            SessionCommand("cmd1", "echo 1", None),
            SessionCommand("cmd2", "echo 2", None),
            SessionCommand("cmd3", "echo 3", None),
        ]
        
        for cmd in commands:
            cli.session_history.append(cmd)
        
        history = cli.get_session_history()
        
        assert len(history) == 3
        assert history[0].natural_language == "cmd1"
        assert history[1].natural_language == "cmd2"
        assert history[2].natural_language == "cmd3"


# Property-Based Tests

@settings(max_examples=100)
@given(input_text=st.text(min_size=1, max_size=1000))
def test_property_input_length_validation_valid(input_text):
    """
    Feature: haunted-terminal-cli, Property 1: Input length validation
    **Validates: Requirements 1.2, 1.3**
    
    For any user input string, if the length is between 1 and 1000 characters,
    the system should accept it.
    """
    cli = HauntedCLI()
    
    # Mock the input to return our test string
    with patch('builtins.input', return_value=input_text):
        result = cli.get_user_input()
        
        # If the input is not empty after stripping, it should be accepted
        if input_text.strip():
            assert result == input_text.strip()
        else:
            # Empty or whitespace-only input should return empty string
            assert result == ""


@settings(max_examples=100)
@given(input_text=st.text(min_size=1001, max_size=2000))
def test_property_input_length_validation_too_long(input_text):
    """
    Feature: haunted-terminal-cli, Property 1: Input length validation
    **Validates: Requirements 1.2, 1.3**
    
    For any user input string over 1000 characters, the system should reject it
    with appropriate messaging.
    """
    cli = HauntedCLI()
    
    # Mock the input to return our test string
    with patch('builtins.input', return_value=input_text):
        result = cli.get_user_input()
        
        # Input over 1000 characters should be rejected (returns empty string)
        assert result == ""


@settings(max_examples=100)
@given(whitespace=st.text(alphabet=' \t\n\r', min_size=1, max_size=100))
def test_property_input_length_validation_empty(whitespace):
    """
    Feature: haunted-terminal-cli, Property 1: Input length validation
    **Validates: Requirements 1.2, 1.3**
    
    For any empty or whitespace-only input, the system should reject it
    with appropriate messaging.
    """
    cli = HauntedCLI()
    
    # Mock the input to return whitespace
    with patch('builtins.input', return_value=whitespace):
        result = cli.get_user_input()
        
        # Empty or whitespace-only input should return empty string
        assert result == ""


@settings(max_examples=100)
@given(
    commands=st.lists(
        st.tuples(
            st.text(min_size=1, max_size=100, alphabet=st.characters(blacklist_categories=('Cs', 'Cc'))),  # natural_language
            st.text(min_size=1, max_size=100, alphabet=st.characters(blacklist_categories=('Cs', 'Cc')))   # shell_command
        ),
        min_size=1,
        max_size=20
    )
)
def test_property_session_history_persistence(commands):
    """
    Feature: haunted-terminal-cli, Property 2: Session history persistence
    **Validates: Requirements 1.5**
    
    For any sequence of commands executed in a session, querying the session
    history should return all executed commands in chronological order.
    """
    cli = HauntedCLI()
    
    # Add commands to session history in order
    for natural_lang, shell_cmd in commands:
        session_cmd = SessionCommand(
            natural_language=natural_lang,
            shell_command=shell_cmd,
            result=None
        )
        cli.session_history.append(session_cmd)
    
    # Retrieve session history
    history = cli.get_session_history()
    
    # Verify all commands are present
    assert len(history) == len(commands)
    
    # Verify chronological order is maintained
    for i, (natural_lang, shell_cmd) in enumerate(commands):
        assert history[i].natural_language == natural_lang
        assert history[i].shell_command == shell_cmd
    
    # Verify it's a copy, not the original list
    assert history is not cli.session_history


@settings(max_examples=100)
@given(
    original_input=st.text(min_size=1, max_size=100, alphabet=st.characters(blacklist_categories=('Cs', 'Cc'))),
    shell_command=st.text(min_size=1, max_size=100, alphabet=st.characters(blacklist_categories=('Cs', 'Cc')))
)
def test_property_command_preview_completeness(original_input, shell_command):
    """
    Feature: haunted-terminal-cli, Property 6: Command preview completeness
    **Validates: Requirements 3.1, 3.2, 3.3**
    
    For any interpreted command, the preview display should contain both the
    original natural language input and the shell command, and should prompt
    for user confirmation.
    """
    cli = HauntedCLI()
    
    # Capture console output
    from io import StringIO
    from rich.console import Console
    
    # Create a string buffer to capture output
    output_buffer = StringIO()
    test_console = Console(file=output_buffer, force_terminal=True, width=120)
    
    # Replace the CLI's theme console with our test console
    original_console = cli.theme.console
    cli.theme.console = test_console
    
    try:
        # Display the command preview
        cli.display_command_preview(original_input, shell_command)
        
        # Get the captured output
        output = output_buffer.getvalue()
        
        # Verify both the original input and shell command are present in the output
        # The output should contain both strings (accounting for ANSI codes and formatting)
        assert original_input in output, f"Original input '{original_input}' not found in preview output"
        assert shell_command in output, f"Shell command '{shell_command}' not found in preview output"
        
        # Verify the output is not empty (something was displayed)
        assert len(output.strip()) > 0, "Command preview produced no output"
        
    finally:
        # Restore original console
        cli.theme.console = original_console


@settings(max_examples=100)
@given(
    error_type=st.sampled_from([
        'ollama_connection',
        'ollama_interpretation',
        'validation',
        'execution',
        'database',
        'unexpected'
    ]),
    user_input=st.text(min_size=1, max_size=100, alphabet=st.characters(blacklist_categories=('Cs', 'Cc')))
)
def test_property_error_recovery(error_type, user_input):
    """
    Feature: haunted-terminal-cli, Property 15: Error recovery
    **Validates: Requirements 7.1, 7.4, 7.5**
    
    For any exception or error that occurs, the system should catch it,
    display a themed error message, log details, and return to the main
    input prompt without crashing.
    """
    from src.ollama_client import OllamaConnectionError, OllamaInterpretationError
    from io import StringIO
    from rich.console import Console
    
    cli = HauntedCLI()
    
    # Capture console output
    output_buffer = StringIO()
    test_console = Console(file=output_buffer, force_terminal=True, width=120)
    original_console = cli.theme.console
    cli.theme.console = test_console
    
    # Mock components to raise specific errors
    mock_ollama = Mock()
    mock_executor = Mock()
    mock_history = Mock()
    
    # Configure mocks based on error type
    if error_type == 'ollama_connection':
        mock_ollama.interpret_command.side_effect = OllamaConnectionError("Connection failed")
    elif error_type == 'ollama_interpretation':
        mock_ollama.interpret_command.side_effect = OllamaInterpretationError("Cannot interpret")
    elif error_type == 'validation':
        mock_ollama.interpret_command.return_value = "echo test"
        mock_executor.validate_syntax.return_value = False
    elif error_type == 'execution':
        mock_ollama.interpret_command.return_value = "echo test"
        mock_executor.validate_syntax.return_value = True
        mock_executor.execute.side_effect = ValueError("Execution failed")
    elif error_type == 'database':
        mock_ollama.interpret_command.return_value = "echo test"
        mock_executor.validate_syntax.return_value = True
        mock_executor.execute.return_value = ExecutionResult(
            command="echo test",
            stdout="test",
            stderr="",
            exit_code=0,
            execution_time=0.1,
            timestamp=datetime.now()
        )
        mock_executor.get_working_directory.return_value = "/tmp"
        mock_history.save_command.side_effect = sqlite3.Error("Database error")
    elif error_type == 'unexpected':
        mock_ollama.interpret_command.side_effect = RuntimeError("Unexpected error")
    
    cli.ollama = mock_ollama
    cli.executor = mock_executor
    cli.history = mock_history
    
    # Mock input to provide user input once, then exit
    input_sequence = [user_input, 'exit']
    input_iter = iter(input_sequence)
    
    try:
        with patch('builtins.input', side_effect=lambda *args: next(input_iter)):
            # Run the CLI - it should handle the error and not crash
            exit_code = cli.run()
            
            # Verify the application didn't crash (returned normally)
            assert exit_code == 0, f"Application crashed with exit code {exit_code}"
            
            # Get the captured output
            output = output_buffer.getvalue()
            
            # Verify an error message was displayed (output should not be empty)
            assert len(output) > 0, "No error message was displayed"
            
            # Verify the application continued running (didn't crash immediately)
            # This is evidenced by the fact that run() completed and returned 0
            assert cli.running == True or exit_code == 0, "Application did not continue running after error"
            
    except StopIteration:
        # This is expected when we run out of inputs
        pass
    except Exception as e:
        # If any exception escapes, the error recovery failed
        pytest.fail(f"Error recovery failed: {type(e).__name__}: {str(e)}")
    finally:
        # Restore original console
        cli.theme.console = original_console


@settings(max_examples=100)
@given(
    command=st.sampled_from([
        "cat /nonexistent_file_xyz_12345.txt",
        "ls /nonexistent_directory_xyz_12345",
        "grep pattern /nonexistent_file_xyz_12345.txt",
        "false",
        "exit 1",
        "test -f /nonexistent_file_xyz_12345.txt"
    ]),
    stderr_content=st.text(
        alphabet=st.characters(blacklist_categories=('Cs', 'Cc')),
        min_size=1,
        max_size=200
    )
)
def test_property_failed_command_stderr_display(command, stderr_content):
    """
    Feature: haunted-terminal-cli, Property 16: Failed command stderr display
    **Validates: Requirements 7.3**
    
    For any command that fails during execution, the system should display
    the stderr output along with helpful context.
    """
    from io import StringIO
    from rich.console import Console
    import re
    
    cli = HauntedCLI()
    
    # Capture console output
    output_buffer = StringIO()
    test_console = Console(file=output_buffer, force_terminal=True, width=120)
    original_console = cli.theme.console
    cli.theme.console = test_console
    
    try:
        # Create a failed execution result with stderr
        failed_result = ExecutionResult(
            command=command,
            stdout="",
            stderr=stderr_content,
            exit_code=1,  # Non-zero exit code indicates failure
            execution_time=0.1,
            timestamp=datetime.now()
        )
        
        # Display the output using the CLI's display method
        cli.display_output(failed_result)
        
        # Get the captured output
        output = output_buffer.getvalue()
        
        # Strip ANSI codes for easier content checking
        ansi_escape = re.compile(r'\x1b\[[0-9;]*m')
        output_no_ansi = ansi_escape.sub('', output)
        
        # Property 1: Output should not be empty (something was displayed)
        assert len(output.strip()) > 0, \
            "Failed command output should not be empty"
        
        # Property 2: The stderr content should be present in the output
        # Check in the version without ANSI codes to avoid formatting issues
        # Note: We strip both because the display system normalizes whitespace
        stderr_normalized = stderr_content.strip()
        if stderr_normalized:  # Only check if there's actual content
            assert stderr_normalized in output_no_ansi, \
                f"stderr content '{stderr_normalized}' should be displayed in output. Got: {output_no_ansi}"
        
        # Property 3: The exit code should be indicated in the output
        # The display should show that the command failed
        assert "1" in output_no_ansi or "failed" in output_no_ansi.lower() or "error" in output_no_ansi.lower(), \
            "Output should indicate command failure (exit code or error message)"
        
        # Property 4: For non-empty stderr, it should be prominently displayed
        # The theme manager should format it in a way that makes it visible
        if stderr_content.strip():
            # Check that stderr is not just hidden or minimized
            # It should be a substantial part of the output
            assert len(output_no_ansi) >= len(stderr_content) * 0.5, \
                "stderr should be prominently displayed, not hidden"
        
    finally:
        # Restore original console
        cli.theme.console = original_console


@settings(max_examples=100)
@given(
    exit_code=st.integers(min_value=1, max_value=255),
    stderr_lines=st.lists(
        st.text(
            alphabet=st.characters(blacklist_categories=('Cs', 'Cc')),
            min_size=1,
            max_size=100
        ),
        min_size=1,
        max_size=10
    )
)
def test_property_failed_command_stderr_display_multiline(exit_code, stderr_lines):
    """
    Feature: haunted-terminal-cli, Property 16: Failed command stderr display
    **Validates: Requirements 7.3**
    
    For any command that fails with multi-line stderr, the system should
    display all stderr lines along with helpful context.
    """
    from io import StringIO
    from rich.console import Console
    import re
    
    cli = HauntedCLI()
    
    # Capture console output
    output_buffer = StringIO()
    test_console = Console(file=output_buffer, force_terminal=True, width=120)
    original_console = cli.theme.console
    cli.theme.console = test_console
    
    try:
        # Join stderr lines with newlines
        stderr_content = "\n".join(stderr_lines)
        
        # Create a failed execution result
        failed_result = ExecutionResult(
            command="test_command",
            stdout="",
            stderr=stderr_content,
            exit_code=exit_code,
            execution_time=0.1,
            timestamp=datetime.now()
        )
        
        # Display the output
        cli.display_output(failed_result)
        
        # Get the captured output
        output = output_buffer.getvalue()
        
        # Strip ANSI codes for easier content checking
        ansi_escape = re.compile(r'\x1b\[[0-9;]*m')
        output_no_ansi = ansi_escape.sub('', output)
        
        # Property 1: All stderr lines should be present in the output
        # Note: We normalize whitespace because the display system does
        for line in stderr_lines:
            line_normalized = line.strip()
            if line_normalized:  # Only check non-empty lines
                assert line_normalized in output_no_ansi, \
                    f"stderr line '{line_normalized}' should be displayed in output"
        
        # Property 2: The exit code should be indicated
        assert str(exit_code) in output_no_ansi or "failed" in output_no_ansi.lower() or "error" in output_no_ansi.lower(), \
            f"Output should indicate failure with exit code {exit_code}"
        
        # Property 3: Multi-line stderr should maintain structure
        # Check that the output contains newlines (preserving structure)
        if len(stderr_lines) > 1:
            # The output should have multiple lines (not collapsed into one)
            output_lines = output_no_ansi.split('\n')
            assert len(output_lines) > 1, \
                "Multi-line stderr should maintain line structure"
        
    finally:
        # Restore original console
        cli.theme.console = original_console


@settings(max_examples=100)
@given(
    command=st.text(
        alphabet=st.characters(blacklist_categories=('Cs', 'Cc')),
        min_size=1,
        max_size=100
    ),
    stdout_content=st.text(
        alphabet=st.characters(blacklist_categories=('Cs', 'Cc')),
        min_size=0,
        max_size=200
    ),
    execution_time=st.floats(min_value=0.001, max_value=10.0)
)
def test_property_success_message_theming(command, stdout_content, execution_time):
    """
    Feature: haunted-terminal-cli, Property 10: Success message theming
    **Validates: Requirements 5.3**
    
    For any successfully executed command, the displayed success message
    should contain themed language elements (magical, mystical references).
    """
    from io import StringIO
    from rich.console import Console
    import re
    
    cli = HauntedCLI()
    
    # Capture console output
    output_buffer = StringIO()
    test_console = Console(file=output_buffer, force_terminal=True, width=120)
    original_console = cli.theme.console
    cli.theme.console = test_console
    
    try:
        # Create a successful execution result
        success_result = ExecutionResult(
            command=command,
            stdout=stdout_content,
            stderr="",
            exit_code=0,  # Zero exit code indicates success
            execution_time=execution_time,
            timestamp=datetime.now()
        )
        
        # Display the output using the CLI's display method
        cli.display_output(success_result)
        
        # Get the captured output
        output = output_buffer.getvalue()
        
        # Strip ANSI codes for easier content checking
        ansi_escape = re.compile(r'\x1b\[[0-9;]*m')
        output_no_ansi = ansi_escape.sub('', output)
        
        # Property 1: Output should not be empty (something was displayed)
        assert len(output.strip()) > 0, \
            "Success message output should not be empty"
        
        # Property 2: The success message should contain magical/mystical themed language
        # According to the theme manager, success messages use "SPELL CAST"
        # This is the magical themed language element required by Requirement 5.3
        magical_terms = [
            "SPELL CAST",  # Primary magical term used in display_success
            "spell",       # Variations that might appear
            "cast",
            "ritual",
            "summoning",
            "magic",
            "mystical",
            "enchant"
        ]
        
        # At least one magical term should be present in the output
        has_magical_theme = any(term.lower() in output_no_ansi.lower() for term in magical_terms)
        assert has_magical_theme, \
            f"Success message should contain magical/mystical themed language. Got: {output_no_ansi}"
        
        # Property 3: The success indicator (checkmark or similar) should be present
        # The theme uses "✓" as the success symbol
        success_indicators = ["✓", "success", "complete", "done"]
        has_success_indicator = any(indicator in output_no_ansi for indicator in success_indicators)
        assert has_success_indicator, \
            f"Success message should contain a success indicator. Got: {output_no_ansi}"
        
        # Property 4: For successful commands, the output should not contain error language
        # Success messages should be positive, not negative
        error_terms = ["failed", "error", "crash", "broken"]
        has_error_language = any(term in output_no_ansi.lower() for term in error_terms)
        assert not has_error_language, \
            f"Success message should not contain error language. Got: {output_no_ansi}"
        
    finally:
        # Restore original console
        cli.theme.console = original_console


@settings(max_examples=100)
@given(
    command=st.text(
        alphabet=st.characters(blacklist_categories=('Cs', 'Cc')),
        min_size=1,
        max_size=100
    ),
    stdout_content=st.text(
        alphabet=st.characters(blacklist_categories=('Cs', 'Cc')),
        min_size=0,
        max_size=200
    ),
    stderr_content=st.text(
        alphabet=st.characters(blacklist_categories=('Cs', 'Cc')),
        min_size=0,
        max_size=200
    ),
    exit_code=st.integers(min_value=0, max_value=255),
    execution_time=st.floats(min_value=0.001, max_value=10.0)
)
def test_property_result_display_with_exit_codes(command, stdout_content, stderr_content, exit_code, execution_time):
    """
    Feature: haunted-terminal-cli, Property 13: Result display with exit codes
    **Validates: Requirements 6.3, 6.4**
    
    For any completed command, the display should show the output and, if the exit code
    is non-zero, should prominently display the exit code with error information.
    """
    from io import StringIO
    from rich.console import Console
    import re
    
    cli = HauntedCLI()
    
    # Capture console output
    output_buffer = StringIO()
    test_console = Console(file=output_buffer, force_terminal=True, width=120)
    original_console = cli.theme.console
    cli.theme.console = test_console
    
    try:
        # Create an execution result with the given parameters
        result = ExecutionResult(
            command=command,
            stdout=stdout_content,
            stderr=stderr_content,
            exit_code=exit_code,
            execution_time=execution_time,
            timestamp=datetime.now()
        )
        
        # Display the output using the CLI's display method
        cli.display_output(result)
        
        # Get the captured output
        output = output_buffer.getvalue()
        
        # Strip ANSI codes for easier content checking
        ansi_escape = re.compile(r'\x1b\[[0-9;]*m')
        output_no_ansi = ansi_escape.sub('', output)
        
        # Property 1: Output should not be empty (something was displayed)
        assert len(output.strip()) > 0, \
            "Result display should not be empty"
        
        # Property 2: If stdout has content, it should be displayed
        if stdout_content and stdout_content.strip():
            # Check that stdout content is present in the output
            # Normalize whitespace for comparison
            stdout_normalized = stdout_content.strip()
            assert stdout_normalized in output_no_ansi, \
                f"stdout content should be displayed. Expected: '{stdout_normalized}' in output"
        
        # Property 3: If exit code is non-zero, it should be prominently displayed
        if exit_code != 0:
            # The exit code should be mentioned in the output
            assert str(exit_code) in output_no_ansi, \
                f"Non-zero exit code {exit_code} should be displayed in output"
            
            # Error-related language should be present for non-zero exit codes
            # Hybrid approach: could be "failed", "partial success", or "exit code"
            error_indicators = ["failed", "error", "exit code", "partial success"]
            has_error_indicator = any(indicator in output_no_ansi.lower() for indicator in error_indicators)
            assert has_error_indicator, \
                f"Non-zero exit code should be accompanied by error indicators. Got: {output_no_ansi}"
        
        # Property 4: If exit code is non-zero and stderr has content, stderr should be displayed
        if exit_code != 0 and stderr_content and stderr_content.strip():
            # Check that stderr content is present in the output
            stderr_normalized = stderr_content.strip()
            assert stderr_normalized in output_no_ansi, \
                f"stderr content should be displayed for failed commands. Expected: '{stderr_normalized}' in output"
        
        # Property 5: If exit code is zero, success indicators should be present
        if exit_code == 0:
            # Success indicators should be present
            success_indicators = ["✓", "success", "spell", "cast"]
            has_success_indicator = any(indicator in output_no_ansi.lower() for indicator in success_indicators)
            assert has_success_indicator, \
                f"Zero exit code should be accompanied by success indicators. Got: {output_no_ansi}"
        
        # Property 6: Execution time should be displayed
        # The execution time should be mentioned somewhere in the output
        # Format could be "0.12s" or similar
        time_str = f"{execution_time:.2f}"
        # Check if the time value appears (may have 's' suffix or be part of larger text)
        assert time_str in output_no_ansi or f"{execution_time:.1f}" in output_no_ansi, \
            f"Execution time should be displayed in output. Expected time around {execution_time:.2f}s"
        
    finally:
        # Restore original console
        cli.theme.console = original_console
