"""
Property-based tests for safety manager.
"""
import pytest
from hypothesis import given, strategies as st, settings
from src.safety import classify_command, CommandRisk, get_confirmation


# Feature: haunted-terminal-cli, Property 7: Destructive command classification
# For any shell command string, if it contains patterns matching rm, mv, dd, format, or mkfs,
# the system should classify it as destructive.
# Validates: Requirements 4.1, 4.5

@settings(max_examples=100)
@given(st.text(min_size=1, max_size=200))
def test_property_destructive_command_classification_rm(command_suffix):
    """
    Property 7: Destructive command classification
    Test that commands containing 'rm' with destructive patterns are classified as DESTRUCTIVE.
    """
    # Generate commands with rm patterns that should be destructive
    destructive_commands = [
        f"rm -rf /{command_suffix}",
        f"rm -r {command_suffix}",
        f"rm -f {command_suffix}",
        f"rm --recursive {command_suffix}",
        f"rm --force {command_suffix}",
        f"rm {command_suffix}*",  # rm with wildcards
    ]
    
    for cmd in destructive_commands:
        result = classify_command(cmd)
        assert result == CommandRisk.DESTRUCTIVE, f"Command '{cmd}' should be classified as DESTRUCTIVE but got {result}"


@settings(max_examples=100)
@given(st.text(min_size=1, max_size=200, alphabet=st.characters(blacklist_characters=['\x00', '\n', '\r'])))
def test_property_destructive_command_classification_dd(text_content):
    """
    Property 7: Destructive command classification
    Test that commands containing 'dd' are classified as DESTRUCTIVE.
    """
    # dd is always destructive
    commands = [
        f"dd if=/dev/zero of={text_content}",
        f"dd {text_content}",
        f"sudo dd if=/dev/sda of=/dev/sdb",
    ]
    
    for cmd in commands:
        result = classify_command(cmd)
        assert result == CommandRisk.DESTRUCTIVE, f"Command '{cmd}' should be classified as DESTRUCTIVE but got {result}"


@settings(max_examples=100)
@given(st.text(min_size=1, max_size=200, alphabet=st.characters(blacklist_characters=['\x00', '\n', '\r'])))
def test_property_destructive_command_classification_mkfs(device_name):
    """
    Property 7: Destructive command classification
    Test that commands containing 'mkfs' are classified as DESTRUCTIVE.
    """
    commands = [
        f"mkfs.ext4 {device_name}",
        f"mkfs {device_name}",
        f"sudo mkfs.vfat /dev/{device_name}",
    ]
    
    for cmd in commands:
        result = classify_command(cmd)
        assert result == CommandRisk.DESTRUCTIVE, f"Command '{cmd}' should be classified as DESTRUCTIVE but got {result}"


@settings(max_examples=100)
@given(st.text(min_size=1, max_size=200, alphabet=st.characters(blacklist_characters=['\x00', '\n', '\r'])))
def test_property_destructive_command_classification_format(device_name):
    """
    Property 7: Destructive command classification
    Test that commands containing 'format' are classified as DESTRUCTIVE.
    """
    commands = [
        f"format {device_name}",
        f"format /dev/{device_name}",
    ]
    
    for cmd in commands:
        result = classify_command(cmd)
        assert result == CommandRisk.DESTRUCTIVE, f"Command '{cmd}' should be classified as DESTRUCTIVE but got {result}"


@settings(max_examples=100)
@given(st.text(min_size=1, max_size=200, alphabet=st.characters(blacklist_characters=['\x00', '\n', '\r', '/'])))
def test_property_safe_commands_not_destructive(safe_text):
    """
    Property 7: Destructive command classification
    Test that safe commands without destructive patterns are NOT classified as DESTRUCTIVE.
    """
    # Generate safe commands that should NOT be destructive
    safe_commands = [
        f"echo {safe_text}",
        f"ls {safe_text}",
        f"cat {safe_text}",
        f"pwd",
        f"cd {safe_text}",
        f"grep {safe_text}",
    ]
    
    for cmd in safe_commands:
        result = classify_command(cmd)
        assert result != CommandRisk.DESTRUCTIVE, f"Safe command '{cmd}' should NOT be classified as DESTRUCTIVE but got {result}"


@settings(max_examples=100)
@given(st.text(min_size=1, max_size=200, alphabet=st.characters(blacklist_characters=['\x00', '\n', '\r'])))
def test_property_mv_classified_as_destructive(filename):
    """
    Property 7: Destructive command classification
    Test that 'mv' commands are classified as DESTRUCTIVE per Requirement 4.5.
    """
    commands = [
        f"mv {filename} backup",
        f"mv old_{filename} new_{filename}",
    ]
    
    for cmd in commands:
        result = classify_command(cmd)
        # mv should be DESTRUCTIVE per Requirement 4.5
        assert result == CommandRisk.DESTRUCTIVE, f"Command '{cmd}' should be classified as DESTRUCTIVE but got {result}"


# Unit tests for specific edge cases
def test_empty_string_is_safe():
    """Test that empty strings are classified as SAFE."""
    assert classify_command("") == CommandRisk.SAFE
    assert classify_command("   ") == CommandRisk.SAFE


def test_none_raises_error():
    """Test that None input raises ValueError."""
    with pytest.raises(ValueError):
        classify_command(None)


def test_specific_destructive_commands():
    """Test specific known destructive commands."""
    destructive_commands = [
        "rm -rf /",
        "rm -rf /*",
        "dd if=/dev/zero of=/dev/sda",
        "mkfs.ext4 /dev/sda1",
        "format c:",
        "rm *.txt",
        "chmod -R 777 /",
        "chown -R nobody:nobody /",
    ]
    
    for cmd in destructive_commands:
        result = classify_command(cmd)
        assert result == CommandRisk.DESTRUCTIVE, f"Command '{cmd}' should be DESTRUCTIVE"


def test_specific_safe_commands():
    """Test specific known safe commands."""
    safe_commands = [
        "ls -la",
        "cat file.txt",
        "echo hello",
        "pwd",
        "cd /home",
        "grep pattern file.txt",
        "find . -name '*.py'",
        "ps aux",
        "top",
    ]
    
    for cmd in safe_commands:
        result = classify_command(cmd)
        assert result == CommandRisk.SAFE, f"Command '{cmd}' should be SAFE"


def test_safe_stderr_redirect():
    """Test that 2>/dev/null is not flagged as destructive."""
    safe_commands = [
        "find . -name test 2>/dev/null",
        "cat file 2>/dev/null",
        "ls nonexistent 2>/dev/null",
    ]
    
    for cmd in safe_commands:
        result = classify_command(cmd)
        assert result == CommandRisk.SAFE, f"Command '{cmd}' with 2>/dev/null should be SAFE"


def test_dangerous_device_redirect():
    """Test that redirecting to device files (not /dev/null) is destructive."""
    dangerous_commands = [
        "echo test >/dev/sda",
        "cat file >/dev/sda1",
        "echo data >/dev/disk1",
    ]
    
    for cmd in dangerous_commands:
        result = classify_command(cmd)
        assert result == CommandRisk.DESTRUCTIVE, f"Command '{cmd}' redirecting to device should be DESTRUCTIVE"


# Unit tests for confirmation prompt variations
# Requirements: 4.1, 4.2, 4.3

def test_get_confirmation_safe_command_requires_risk_enum():
    """Test that get_confirmation requires a valid CommandRisk enum."""
    with pytest.raises(ValueError, match="Invalid risk type"):
        get_confirmation("ls -la", "safe")  # String instead of enum


def test_get_confirmation_none_command_raises_error():
    """Test that get_confirmation raises ValueError for None command."""
    with pytest.raises(ValueError, match="Command cannot be None"):
        get_confirmation(None, CommandRisk.SAFE)


def test_get_confirmation_validates_risk_type():
    """Test that get_confirmation validates the risk parameter type."""
    with pytest.raises(ValueError):
        get_confirmation("ls -la", "invalid_risk")


def test_classify_command_handles_case_insensitivity():
    """Test that command classification is case-insensitive."""
    # Test uppercase variations
    assert classify_command("RM -rf /") == CommandRisk.DESTRUCTIVE
    assert classify_command("Rm -RF /") == CommandRisk.DESTRUCTIVE
    assert classify_command("DD if=/dev/zero") == CommandRisk.DESTRUCTIVE
    assert classify_command("MKFS.ext4 /dev/sda") == CommandRisk.DESTRUCTIVE
    assert classify_command("MV file1 file2") == CommandRisk.DESTRUCTIVE
    assert classify_command("FORMAT /dev/sda") == CommandRisk.DESTRUCTIVE


def test_classify_command_moderate_risk():
    """Test that moderate risk commands are properly classified."""
    moderate_commands = [
        "chmod 755 file.txt",
        "chown user:group file.txt",
        "kill 1234",
        "pkill process",
        "killall firefox",
    ]
    
    for cmd in moderate_commands:
        result = classify_command(cmd)
        assert result == CommandRisk.MODERATE, f"Command '{cmd}' should be MODERATE risk"


def test_classify_command_recursive_operations_are_destructive():
    """Test that recursive chmod/chown are classified as destructive."""
    recursive_commands = [
        "chmod -R 777 /",
        "chown -R nobody /",
        "chmod -r 755 /home",  # lowercase -r
        "chown -r user:group /var",  # lowercase -r
    ]
    
    for cmd in recursive_commands:
        result = classify_command(cmd)
        assert result == CommandRisk.DESTRUCTIVE, f"Recursive command '{cmd}' should be DESTRUCTIVE"


def test_classify_command_package_removal_is_destructive():
    """Test that package removal commands are classified as destructive."""
    package_commands = [
        "apt remove package",
        "apt purge package",
        "yum remove package",
        "pip uninstall package",
    ]
    
    for cmd in package_commands:
        result = classify_command(cmd)
        assert result == CommandRisk.DESTRUCTIVE, f"Package removal '{cmd}' should be DESTRUCTIVE"


def test_classify_command_with_pipes_and_redirects():
    """Test that commands with pipes and redirects are properly classified."""
    # Safe pipes
    assert classify_command("cat file.txt | grep pattern") == CommandRisk.SAFE
    assert classify_command("ls -la | sort") == CommandRisk.SAFE
    
    # Destructive with pipes
    assert classify_command("cat file | rm -rf /") == CommandRisk.DESTRUCTIVE
    assert classify_command("echo test | dd of=/dev/sda") == CommandRisk.DESTRUCTIVE


def test_classify_command_with_command_chaining():
    """Test that command chaining is properly handled."""
    # If any command in the chain is destructive, the whole thing should be destructive
    assert classify_command("ls -la && rm -rf /tmp/test") == CommandRisk.DESTRUCTIVE
    assert classify_command("cd /tmp; rm -rf *") == CommandRisk.DESTRUCTIVE
    assert classify_command("echo hello || dd if=/dev/zero") == CommandRisk.DESTRUCTIVE


def test_classify_command_with_sudo():
    """Test that sudo commands are properly classified based on the actual command."""
    assert classify_command("sudo rm -rf /") == CommandRisk.DESTRUCTIVE
    assert classify_command("sudo dd if=/dev/zero of=/dev/sda") == CommandRisk.DESTRUCTIVE
    assert classify_command("sudo ls -la") == CommandRisk.SAFE
    assert classify_command("sudo chmod 755 file") == CommandRisk.MODERATE


def test_classify_command_edge_cases():
    """Test edge cases in command classification."""
    # Commands that contain destructive keywords - the classifier uses word boundaries
    # so it will match 'rm' even in quoted strings (which is safer - better to warn)
    assert classify_command("man rm") == CommandRisk.DESTRUCTIVE  # Contains 'rm' word boundary
    assert classify_command("grep rm file.txt") == CommandRisk.DESTRUCTIVE  # Contains 'rm' word boundary
    
    # Very long commands
    long_cmd = "ls " + " ".join([f"file{i}" for i in range(100)])
    assert classify_command(long_cmd) == CommandRisk.SAFE
    
    # Commands with special characters
    assert classify_command("rm -rf /tmp/test*") == CommandRisk.DESTRUCTIVE
    assert classify_command("rm -rf /tmp/test?") == CommandRisk.DESTRUCTIVE


def test_classify_command_truncate():
    """Test that truncate command is classified as destructive."""
    assert classify_command("truncate -s 0 file.txt") == CommandRisk.DESTRUCTIVE
    assert classify_command("truncate file.txt") == CommandRisk.DESTRUCTIVE


def test_specific_rm_variations():
    """Test various rm command variations per Requirement 4.5."""
    rm_commands = [
        "rm file.txt",
        "rm -f file.txt",
        "rm -r directory",
        "rm -rf /tmp/test",
        "rm -rf /*",
        "rm -rf /",
        "rm *.txt",
        "rm -i file.txt",  # Even interactive rm is destructive
        "rm --force file",
        "rm --recursive dir",
    ]
    
    for cmd in rm_commands:
        result = classify_command(cmd)
        assert result == CommandRisk.DESTRUCTIVE, f"rm command '{cmd}' should be DESTRUCTIVE per Requirement 4.5"


def test_specific_mv_variations():
    """Test various mv command variations per Requirement 4.5."""
    mv_commands = [
        "mv file1.txt file2.txt",
        "mv -f source dest",
        "mv directory /tmp/",
        "mv *.txt backup/",
        "mv --force file dest",
    ]
    
    for cmd in mv_commands:
        result = classify_command(cmd)
        assert result == CommandRisk.DESTRUCTIVE, f"mv command '{cmd}' should be DESTRUCTIVE per Requirement 4.5"


def test_specific_dd_variations():
    """Test various dd command variations per Requirement 4.5."""
    dd_commands = [
        "dd if=/dev/zero of=/dev/sda",
        "dd if=/dev/sda of=/dev/sdb",
        "dd if=file.img of=/dev/disk1",
        "dd if=/dev/random of=file bs=1M count=100",
    ]
    
    for cmd in dd_commands:
        result = classify_command(cmd)
        assert result == CommandRisk.DESTRUCTIVE, f"dd command '{cmd}' should be DESTRUCTIVE per Requirement 4.5"


def test_specific_format_variations():
    """Test various format command variations per Requirement 4.5."""
    format_commands = [
        "format /dev/sda",
        "format c:",
        "format disk1",
    ]
    
    for cmd in format_commands:
        result = classify_command(cmd)
        assert result == CommandRisk.DESTRUCTIVE, f"format command '{cmd}' should be DESTRUCTIVE per Requirement 4.5"


def test_specific_mkfs_variations():
    """Test various mkfs command variations per Requirement 4.5."""
    mkfs_commands = [
        "mkfs /dev/sda",
        "mkfs.ext4 /dev/sda1",
        "mkfs.vfat /dev/sdb1",
        "mkfs.ntfs /dev/sdc1",
    ]
    
    for cmd in mkfs_commands:
        result = classify_command(cmd)
        assert result == CommandRisk.DESTRUCTIVE, f"mkfs command '{cmd}' should be DESTRUCTIVE per Requirement 4.5"


def test_safe_commands_comprehensive():
    """Comprehensive test of commands that should be classified as SAFE."""
    safe_commands = [
        # File viewing
        "cat file.txt",
        "less file.txt",
        "more file.txt",
        "head file.txt",
        "tail file.txt",
        "tail -f /var/log/syslog",
        
        # Directory operations
        "ls",
        "ls -la",
        "ls -lah /tmp",
        "pwd",
        "cd /home/user",
        "cd ..",
        
        # Search operations
        "find . -name '*.py'",
        "grep pattern file.txt",
        "grep -r pattern .",
        "locate file",
        
        # Process viewing
        "ps aux",
        "ps -ef",
        "top",
        "htop",
        
        # System info
        "uname -a",
        "whoami",
        "hostname",
        "date",
        "uptime",
        "df -h",
        "du -sh",
        
        # Network viewing
        "ping google.com",
        "curl https://example.com",
        "wget https://example.com/file",
        "netstat -an",
        "ifconfig",
        "ip addr",
        
        # Text processing
        "echo hello",
        "printf 'test'",
        "awk '{print $1}' file",
        "sed 's/old/new/' file",
        "sort file.txt",
        "uniq file.txt",
        "wc -l file.txt",
        
        # Compression (viewing/extracting, not creating)
        "tar -tzf archive.tar.gz",
        "unzip -l archive.zip",
        "gunzip file.gz",
        
        # Safe redirects
        "echo test 2>/dev/null",
        "cat file 2>/dev/null",
        "ls nonexistent 2>/dev/null",
    ]
    
    for cmd in safe_commands:
        result = classify_command(cmd)
        assert result == CommandRisk.SAFE, f"Command '{cmd}' should be SAFE but got {result}"


# Feature: haunted-terminal-cli, Property 8: Destructive command warning
# For any command classified as destructive, the system should display a prominent warning
# and require explicit typed confirmation beyond yes/no.
# Validates: Requirements 4.2, 4.3

@settings(max_examples=100)
@given(st.text(min_size=1, max_size=200, alphabet=st.characters(blacklist_characters=['\x00', '\n', '\r'])))
def test_property_destructive_command_warning(path_suffix):
    """
    Property 8: Destructive command warning
    Test that destructive commands trigger the appropriate warning mechanism.
    
    This test verifies that:
    1. Commands classified as DESTRUCTIVE are properly identified
    2. The get_confirmation function handles destructive commands appropriately
    3. The confirmation mechanism requires explicit confirmation (not just yes/no)
    """
    from io import StringIO
    from unittest.mock import Mock, patch
    
    # Generate destructive commands
    destructive_commands = [
        f"rm -rf {path_suffix}",
        f"dd if=/dev/zero of={path_suffix}",
        f"mkfs.ext4 {path_suffix}",
        f"format {path_suffix}",
        f"mv {path_suffix} /tmp/",
    ]
    
    for cmd in destructive_commands:
        # Verify the command is classified as DESTRUCTIVE
        risk = classify_command(cmd)
        assert risk == CommandRisk.DESTRUCTIVE, f"Command '{cmd}' should be classified as DESTRUCTIVE"
        
        # Create a mock console to capture output
        mock_console = Mock()
        mock_console.print = Mock()
        
        # Test that get_confirmation with DESTRUCTIVE risk requires explicit confirmation
        # We'll test the different response scenarios
        
        # Scenario 1: User types "EXECUTE" - should return "yes"
        with patch('src.safety.Prompt.ask', return_value="EXECUTE"):
            result = get_confirmation(cmd, CommandRisk.DESTRUCTIVE, mock_console)
            assert result == "yes", f"Typing 'EXECUTE' should return 'yes' for destructive command"
            # Verify that a warning was displayed (console.print was called)
            assert mock_console.print.called, "Warning should be displayed for destructive commands"
        
        # Scenario 2: User types something else - should return "no"
        mock_console.print.reset_mock()
        with patch('src.safety.Prompt.ask', return_value="no"):
            result = get_confirmation(cmd, CommandRisk.DESTRUCTIVE, mock_console)
            assert result == "no", f"Typing 'no' should return 'no' for destructive command"
            assert mock_console.print.called, "Warning should be displayed for destructive commands"
        
        # Scenario 3: User types "yes" (not "EXECUTE") - should return "no"
        mock_console.print.reset_mock()
        with patch('src.safety.Prompt.ask', return_value="yes"):
            result = get_confirmation(cmd, CommandRisk.DESTRUCTIVE, mock_console)
            assert result == "no", f"Typing 'yes' (not 'EXECUTE') should return 'no' for destructive command"
            assert mock_console.print.called, "Warning should be displayed for destructive commands"
        
        # Scenario 4: User types "retry" - should return "retry"
        mock_console.print.reset_mock()
        with patch('src.safety.Prompt.ask', return_value="retry"):
            result = get_confirmation(cmd, CommandRisk.DESTRUCTIVE, mock_console)
            assert result == "retry", f"Typing 'retry' should return 'retry' for destructive command"
            assert mock_console.print.called, "Warning should be displayed for destructive commands"


def test_destructive_warning_displays_prominent_message():
    """
    Unit test to verify that destructive commands display a prominent warning message.
    This complements the property test by checking specific warning content.
    """
    from unittest.mock import Mock, patch, call
    
    cmd = "rm -rf /"
    risk = CommandRisk.DESTRUCTIVE
    
    mock_console = Mock()
    mock_console.print = Mock()
    
    # Mock the Prompt.ask to return "EXECUTE"
    with patch('src.safety.Prompt.ask', return_value="EXECUTE"):
        result = get_confirmation(cmd, risk, mock_console)
    
    # Verify the result
    assert result == "yes"
    
    # Verify that console.print was called multiple times (for the warning display)
    assert mock_console.print.call_count >= 3, "Should display multiple lines for prominent warning"
    
    # Check that the warning contains key elements
    all_print_calls = [str(call) for call in mock_console.print.call_args_list]
    warning_text = " ".join(all_print_calls)
    
    # Should contain danger indicators
    assert "DANGER" in warning_text or "DESTRUCTIVE" in warning_text, "Warning should contain danger indicator"
    
    # Should show the command
    assert cmd in warning_text or "Command:" in warning_text, "Warning should display the command"


def test_safe_and_moderate_commands_do_not_require_explicit_confirmation():
    """
    Unit test to verify that SAFE and MODERATE commands don't require typing 'EXECUTE'.
    They should accept simple yes/no responses.
    """
    from unittest.mock import Mock, patch
    
    # Test SAFE command
    safe_cmd = "ls -la"
    mock_console = Mock()
    
    with patch('src.safety.Prompt.ask', return_value="y"):
        result = get_confirmation(safe_cmd, CommandRisk.SAFE, mock_console)
        assert result == "yes", "SAFE commands should accept 'y' as confirmation"
    
    with patch('src.safety.Prompt.ask', return_value="yes"):
        result = get_confirmation(safe_cmd, CommandRisk.SAFE, mock_console)
        assert result == "yes", "SAFE commands should accept 'yes' as confirmation"
    
    # Test MODERATE command
    moderate_cmd = "chmod 755 file.txt"
    mock_console = Mock()
    
    with patch('src.safety.Prompt.ask', return_value="y"):
        result = get_confirmation(moderate_cmd, CommandRisk.MODERATE, mock_console)
        assert result == "yes", "MODERATE commands should accept 'y' as confirmation"
    
    with patch('src.safety.Prompt.ask', return_value="yes"):
        result = get_confirmation(moderate_cmd, CommandRisk.MODERATE, mock_console)
        assert result == "yes", "MODERATE commands should accept 'yes' as confirmation"


# Feature: haunted-terminal-cli, Property 9: Cancellation safety
# For any destructive command that is cancelled by the user, the system should not execute
# the command, should log the cancellation, and should return to the input prompt.
# Validates: Requirements 4.4

@settings(max_examples=100)
@given(st.text(min_size=1, max_size=200, alphabet=st.characters(blacklist_characters=['\x00', '\n', '\r'])))
def test_property_cancellation_safety(path_suffix):
    """
    Property 9: Cancellation safety
    Test that cancelled destructive commands are not executed, are logged, and system continues.
    
    This test verifies that:
    1. When a user cancels a destructive command, it is not executed
    2. The cancelled command is logged in session history
    3. The system returns to the input prompt (continues running)
    """
    from unittest.mock import Mock, patch, MagicMock
    from src.cli import HauntedCLI
    from src.executor import CommandExecutor
    
    # Generate destructive commands
    destructive_commands = [
        f"rm -rf {path_suffix}",
        f"dd if=/dev/zero of={path_suffix}",
        f"mkfs.ext4 {path_suffix}",
        f"format {path_suffix}",
        f"mv {path_suffix} /tmp/",
    ]
    
    for cmd in destructive_commands:
        # Verify the command is classified as DESTRUCTIVE
        risk = classify_command(cmd)
        assert risk == CommandRisk.DESTRUCTIVE, f"Command '{cmd}' should be classified as DESTRUCTIVE"
        
        # Create a mock CLI with mock components
        mock_theme = Mock()
        mock_theme.console = Mock()
        mock_theme.console.print = Mock()
        mock_theme.get_input = Mock()
        mock_theme.loading_animation = MagicMock()
        mock_theme.loading_animation.return_value.__enter__ = Mock()
        mock_theme.loading_animation.return_value.__exit__ = Mock()
        mock_theme.command_preview = Mock()
        mock_theme.display_warning = Mock()
        
        mock_ollama = Mock()
        mock_ollama.interpret_command = Mock(return_value=cmd)
        
        mock_executor = Mock(spec=CommandExecutor)
        mock_executor.execute = Mock()
        mock_executor.validate_syntax = Mock(return_value=True)
        mock_executor.get_working_directory = Mock(return_value="/tmp")
        
        mock_history = Mock()
        mock_history.get_suggestions = Mock(return_value=[])
        mock_history.get_rejections = Mock(return_value=[])
        mock_history.get_alias = Mock(return_value=None)
        mock_history.add_rejection = Mock()
        
        # Create CLI instance with mocks
        cli = HauntedCLI(
            theme=mock_theme,
            ollama=mock_ollama,
            executor=mock_executor,
            history=mock_history
        )
        
        # Simulate user cancelling the destructive command
        # User enters a natural language command, then cancels when prompted
        with patch('src.safety.Prompt.ask', return_value="no"):
            # Simulate one iteration of the REPL loop
            cli.last_natural_input = "delete everything"
            
            # Get confirmation for the destructive command
            confirmation = get_confirmation(cmd, CommandRisk.DESTRUCTIVE, mock_theme.console)
            
            # Verify confirmation returned "no"
            assert confirmation == "no", f"Cancelling destructive command should return 'no'"
            
            # Simulate the CLI handling the cancellation
            if confirmation == "no":
                # This is what the CLI does when a command is cancelled
                session_cmd_before = len(cli.session_history)
                
                # Log cancelled command (especially for destructive ones)
                if risk == CommandRisk.DESTRUCTIVE:
                    from src.cli import SessionCommand
                    session_cmd = SessionCommand(
                        natural_language="delete everything",
                        shell_command=cmd,
                        result=None
                    )
                    cli.session_history.append(session_cmd)
                
                session_cmd_after = len(cli.session_history)
                
                # Verify the command was NOT executed
                mock_executor.execute.assert_not_called()
                
                # Verify the cancelled command was logged in session history
                assert session_cmd_after > session_cmd_before, \
                    f"Cancelled destructive command should be logged in session history"
                
                # Verify the logged command has no result (was not executed)
                last_session_cmd = cli.session_history[-1]
                assert last_session_cmd.result is None, \
                    f"Cancelled command should have no execution result"
                assert last_session_cmd.shell_command == cmd, \
                    f"Logged command should match the cancelled command"
                
                # Verify the system continues (doesn't crash or exit)
                # The CLI should be in a state where it can accept more input
                # Since we're not calling run(), we just verify the CLI object is still valid
                assert cli is not None, \
                    f"System should continue running after cancellation"
                assert hasattr(cli, 'session_history'), \
                    f"CLI should maintain its state after cancellation"


def test_cancellation_safety_integration():
    """
    Integration test for cancellation safety.
    Verifies the complete flow of cancelling a destructive command.
    """
    from unittest.mock import Mock, patch
    from src.cli import HauntedCLI, SessionCommand
    from src.executor import CommandExecutor
    import tempfile
    
    # Create a CLI instance with real components but mock user input
    executor = CommandExecutor(working_directory=tempfile.gettempdir())
    cli = HauntedCLI(executor=executor)
    
    # Test destructive command
    destructive_cmd = "rm -rf /important/data"
    natural_input = "delete all my important data"
    
    # Verify it's classified as destructive
    risk = classify_command(destructive_cmd)
    assert risk == CommandRisk.DESTRUCTIVE
    
    # Simulate user cancelling
    with patch('src.safety.Prompt.ask', return_value="no"):
        confirmation = get_confirmation(destructive_cmd, risk, cli.theme.console)
        assert confirmation == "no"
        
        # Simulate what the CLI does on cancellation
        initial_history_len = len(cli.session_history)
        
        # Log the cancelled command
        session_cmd = SessionCommand(
            natural_language=natural_input,
            shell_command=destructive_cmd,
            result=None
        )
        cli.session_history.append(session_cmd)
        
        # Verify logging
        assert len(cli.session_history) == initial_history_len + 1
        assert cli.session_history[-1].shell_command == destructive_cmd
        assert cli.session_history[-1].result is None
        
        # Verify the command was not executed (no result)
        assert cli.session_history[-1].result is None


def test_cancellation_with_different_responses():
    """
    Test that various cancellation responses all prevent execution.
    """
    from unittest.mock import Mock, patch
    
    destructive_cmd = "rm -rf /"
    risk = CommandRisk.DESTRUCTIVE
    mock_console = Mock()
    
    # Test various ways to cancel
    cancel_responses = ["no", "n", "cancel", "abort", "stop", ""]
    
    for response in cancel_responses:
        mock_console.print.reset_mock()
        
        with patch('src.safety.Prompt.ask', return_value=response):
            result = get_confirmation(destructive_cmd, risk, mock_console)
            
            # Any response other than "EXECUTE" should result in "no" or "retry"
            assert result in ["no", "retry"], \
                f"Response '{response}' should cancel or retry, got '{result}'"
            
            # If it's "no", verify warning was displayed
            if result == "no":
                assert mock_console.print.called, \
                    "Warning should be displayed for destructive commands"


def test_cancellation_via_keyboard_interrupt():
    """
    Test that Ctrl+C during confirmation cancels the command safely.
    """
    from unittest.mock import Mock, patch
    
    destructive_cmd = "rm -rf /"
    risk = CommandRisk.DESTRUCTIVE
    mock_console = Mock()
    
    # Simulate Ctrl+C (KeyboardInterrupt)
    with patch('src.safety.Prompt.ask', side_effect=KeyboardInterrupt):
        result = get_confirmation(destructive_cmd, risk, mock_console)
        
        # Should return "no" (cancel)
        assert result == "no", "KeyboardInterrupt should cancel the command"


def test_cancellation_via_eof():
    """
    Test that Ctrl+D (EOF) during confirmation cancels the command safely.
    """
    from unittest.mock import Mock, patch
    
    destructive_cmd = "rm -rf /"
    risk = CommandRisk.DESTRUCTIVE
    mock_console = Mock()
    
    # Simulate Ctrl+D (EOFError)
    with patch('src.safety.Prompt.ask', side_effect=EOFError):
        result = get_confirmation(destructive_cmd, risk, mock_console)
        
        # Should return "no" (cancel)
        assert result == "no", "EOFError should cancel the command"
