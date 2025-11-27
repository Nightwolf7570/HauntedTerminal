"""
Tests for the history manager.
"""

import os
import sqlite3
import tempfile
from datetime import datetime
from pathlib import Path

import pytest
from hypothesis import given, strategies as st

from src.history import HistoryManager, HistoryEntry


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    
    yield db_path
    
    # Cleanup
    if os.path.exists(db_path):
        os.unlink(db_path)


def test_initialize_db_creates_tables(temp_db):
    """Test that initialize_db creates the necessary tables."""
    manager = HistoryManager(db_path=temp_db)
    
    # Verify the database file was created
    assert os.path.exists(temp_db)
    
    # Verify we can query the table (it exists)
    import sqlite3
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='command_history'")
    result = cursor.fetchone()
    conn.close()
    
    assert result is not None
    assert result[0] == "command_history"


def test_save_command_persists_data(temp_db):
    """Test that save_command stores command data correctly."""
    manager = HistoryManager(db_path=temp_db)
    
    # Save a command
    manager.save_command(
        natural_language="list files",
        shell_command="ls -la",
        exit_code=0,
        execution_time=0.5,
        working_directory="/tmp"
    )
    
    # Verify it was saved
    recent = manager.get_recent_commands(limit=1)
    assert len(recent) == 1
    assert recent[0].natural_language == "list files"
    assert recent[0].shell_command == "ls -la"
    assert recent[0].exit_code == 0
    assert recent[0].execution_time == 0.5
    assert recent[0].working_directory == "/tmp"


def test_get_recent_commands_returns_in_order(temp_db):
    """Test that get_recent_commands returns commands in chronological order."""
    manager = HistoryManager(db_path=temp_db)
    
    # Save multiple commands
    manager.save_command("first command", "echo 1", 0, 0.1, working_directory="/tmp")
    manager.save_command("second command", "echo 2", 0, 0.2, working_directory="/tmp")
    manager.save_command("third command", "echo 3", 0, 0.3, working_directory="/tmp")
    
    # Get recent commands
    recent = manager.get_recent_commands(limit=3)
    
    assert len(recent) == 3
    assert recent[0].natural_language == "third command"
    assert recent[1].natural_language == "second command"
    assert recent[2].natural_language == "first command"


def test_get_suggestions_finds_similar_commands(temp_db):
    """Test that get_suggestions finds commands with similar natural language."""
    manager = HistoryManager(db_path=temp_db)
    
    # Save commands with different natural language
    manager.save_command("list python files", "find . -name '*.py'", 0, 0.5, working_directory="/tmp")
    manager.save_command("list all files", "ls -la", 0, 0.3, working_directory="/tmp")
    manager.save_command("delete old files", "rm old.txt", 0, 0.2, working_directory="/tmp")
    
    # Search for commands containing "list"
    suggestions = manager.get_suggestions("list", limit=5)
    
    assert len(suggestions) == 2
    # Both should contain "list" in natural language
    for entry in suggestions:
        assert "list" in entry.natural_language.lower()


def test_get_suggestions_orders_by_frequency_and_recency(temp_db):
    """Test that suggestions are ordered by frequency and recency."""
    manager = HistoryManager(db_path=temp_db)
    
    # Save the same command multiple times
    manager.save_command("list files", "ls", 0, 0.1, working_directory="/tmp")
    manager.save_command("list files", "ls", 0, 0.1, working_directory="/tmp")
    manager.save_command("list files", "ls", 0, 0.1, working_directory="/tmp")
    
    # Save a different command once
    manager.save_command("list directories", "ls -d */", 0, 0.1, working_directory="/tmp")
    
    # Search for "list"
    suggestions = manager.get_suggestions("list", limit=5)
    
    # The more frequent command should come first
    assert len(suggestions) >= 1
    assert suggestions[0].shell_command == "ls"


def test_save_command_uses_current_directory_when_none(temp_db):
    """Test that save_command uses current directory when working_directory is None."""
    manager = HistoryManager(db_path=temp_db)
    
    # Change to a known directory that exists
    test_dir = tempfile.gettempdir()
    original_dir = None
    try:
        original_dir = os.getcwd()
    except FileNotFoundError:
        pass
    
    os.chdir(test_dir)
    
    try:
        # Get the actual current directory after chdir (may be resolved symlink)
        actual_cwd = os.getcwd()
        
        manager.save_command(
            natural_language="test command",
            shell_command="echo test",
            exit_code=0,
            execution_time=0.1,
            working_directory=None
        )
        
        recent = manager.get_recent_commands(limit=1)
        assert len(recent) == 1
        assert recent[0].working_directory == actual_cwd
    finally:
        if original_dir:
            try:
                os.chdir(original_dir)
            except (FileNotFoundError, OSError):
                pass


def test_get_recent_commands_respects_limit(temp_db):
    """Test that get_recent_commands respects the limit parameter."""
    manager = HistoryManager(db_path=temp_db)
    
    # Save 10 commands
    for i in range(10):
        manager.save_command(f"command {i}", f"echo {i}", 0, 0.1, working_directory="/tmp")
    
    # Request only 5
    recent = manager.get_recent_commands(limit=5)
    
    assert len(recent) == 5


def test_get_suggestions_respects_limit(temp_db):
    """Test that get_suggestions respects the limit parameter."""
    manager = HistoryManager(db_path=temp_db)
    
    # Save 10 commands with "list" in them
    for i in range(10):
        manager.save_command(f"list files {i}", f"ls {i}", 0, 0.1, working_directory="/tmp")
    
    # Request only 3
    suggestions = manager.get_suggestions("list", limit=3)
    
    assert len(suggestions) == 3

def test_get_directory_suggestions(temp_db):
    """Test retrieval of commands by directory."""
    manager = HistoryManager(db_path=temp_db)
    
    # Save commands in different directories
    manager.save_command("cmd1", "echo 1", 0, 0.1, working_directory="/dir1")
    manager.save_command("cmd1", "echo 1", 0, 0.1, working_directory="/dir1") # Frequent
    manager.save_command("cmd2", "echo 2", 0, 0.1, working_directory="/dir2")
    
    # Suggest for /dir1
    suggestions = manager.get_directory_suggestions("/dir1")
    assert len(suggestions) == 1
    assert suggestions[0].shell_command == "echo 1"
    assert suggestions[0].working_directory == "/dir1"
    
    # Suggest for /dir2
    suggestions = manager.get_directory_suggestions("/dir2")
    assert len(suggestions) == 1
    assert suggestions[0].shell_command == "echo 2"

def test_preferences(temp_db):
    """Test preference setting and getting."""
    manager = HistoryManager(db_path=temp_db)
    
    manager.set_preference("theme", "dark")
    assert manager.get_preference("theme") == "dark"
    assert manager.get_preference("font") is None
    assert manager.get_preference("font", "default") == "default"
    
    # Update preference
    manager.set_preference("theme", "light")
    assert manager.get_preference("theme") == "light"


# Error Handling Tests (Task 9.3)

def test_database_initialization_error_with_invalid_path():
    """Test that database initialization fails gracefully with invalid path."""
    # Try to create database in a path that doesn't exist and can't be created
    invalid_path = "/nonexistent/path/that/cannot/be/created/history.db"
    
    with pytest.raises((sqlite3.Error, RuntimeError)):
        manager = HistoryManager(db_path=invalid_path)


def test_save_command_with_corrupted_database(temp_db):
    """Test graceful degradation when saving to corrupted database."""
    manager = HistoryManager(db_path=temp_db)
    
    # Corrupt the database by writing invalid data
    with open(temp_db, 'w') as f:
        f.write("This is not a valid SQLite database")
    
    # Attempting to save should raise an error
    with pytest.raises((sqlite3.Error, RuntimeError)):
        manager.save_command(
            natural_language="test command",
            shell_command="echo test",
            exit_code=0,
            execution_time=0.1,
            working_directory="/tmp"
        )


def test_get_suggestions_with_database_error(temp_db):
    """Test that get_suggestions handles database errors gracefully."""
    manager = HistoryManager(db_path=temp_db)
    
    # Save some commands first
    manager.save_command("list files", "ls", 0, 0.1, working_directory="/tmp")
    
    # Corrupt the database
    with open(temp_db, 'w') as f:
        f.write("corrupted")
    
    # Attempting to get suggestions should raise an error
    with pytest.raises((sqlite3.Error, RuntimeError)):
        manager.get_suggestions("list")


def test_get_recent_commands_with_database_error(temp_db):
    """Test that get_recent_commands handles database errors gracefully."""
    manager = HistoryManager(db_path=temp_db)
    
    # Save some commands first
    manager.save_command("test", "echo test", 0, 0.1, working_directory="/tmp")
    
    # Corrupt the database
    with open(temp_db, 'w') as f:
        f.write("corrupted")
    
    # Attempting to get recent commands should raise an error
    with pytest.raises((sqlite3.Error, RuntimeError)):
        manager.get_recent_commands()


def test_save_command_with_invalid_parameters():
    """Test that save_command validates input parameters."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    
    try:
        manager = HistoryManager(db_path=db_path)
        
        # Test empty natural language
        with pytest.raises(ValueError, match="natural_language cannot be empty"):
            manager.save_command("", "echo test", 0, 0.1)
        
        # Test empty shell command
        with pytest.raises(ValueError, match="shell_command cannot be empty"):
            manager.save_command("test", "", 0, 0.1)
        
        # Test negative execution time
        with pytest.raises(ValueError, match="execution_time cannot be negative"):
            manager.save_command("test", "echo test", 0, -1.0)
    
    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)


def test_get_suggestions_with_invalid_parameters(temp_db):
    """Test that get_suggestions validates input parameters."""
    manager = HistoryManager(db_path=temp_db)
    
    # Test empty natural language
    with pytest.raises(ValueError, match="natural_language cannot be empty"):
        manager.get_suggestions("")
    
    # Test invalid limit
    with pytest.raises(ValueError, match="limit must be positive"):
        manager.get_suggestions("test", limit=0)
    
    with pytest.raises(ValueError, match="limit must be positive"):
        manager.get_suggestions("test", limit=-1)


def test_get_recent_commands_with_invalid_limit(temp_db):
    """Test that get_recent_commands validates limit parameter."""
    manager = HistoryManager(db_path=temp_db)
    
    # Test invalid limit
    with pytest.raises(ValueError, match="limit must be positive"):
        manager.get_recent_commands(limit=0)
    
    with pytest.raises(ValueError, match="limit must be positive"):
        manager.get_recent_commands(limit=-1)


# Property-Based Tests

from hypothesis import settings

@settings(max_examples=100)
@given(
    natural_language=st.text(alphabet=st.characters(blacklist_categories=('Cs', 'Cc')), min_size=1, max_size=500).filter(lambda x: x.strip()),
    shell_command=st.text(alphabet=st.characters(blacklist_categories=('Cs', 'Cc')), min_size=1, max_size=500).filter(lambda x: x.strip()),
    exit_code=st.integers(min_value=0, max_value=255),
    execution_time=st.floats(min_value=0.001, max_value=3600.0, allow_nan=False, allow_infinity=False),
    working_directory=st.one_of(
        st.just("/tmp"),
        st.just("/home/user"),
        st.just("/var/log"),
        st.text(alphabet=st.characters(whitelist_categories=('L', 'N')), min_size=1, max_size=50).map(lambda x: f"/{x}")
    )
)
def test_property_command_persistence(natural_language, shell_command, exit_code, execution_time, working_directory):
    """
    Feature: haunted-terminal-cli, Property 18: Command persistence
    
    Property: For any successfully executed command, the system should persist a record 
    containing the natural language input, shell command, timestamp, working directory, 
    exit code, and execution time to the SQLite database.
    
    Validates: Requirements 11.1, 11.2
    """
    # Create a temporary database for this test
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    
    try:
        manager = HistoryManager(db_path=db_path)
        
        # Save the command
        manager.save_command(
            natural_language=natural_language,
            shell_command=shell_command,
            exit_code=exit_code,
            execution_time=execution_time,
            working_directory=working_directory
        )
        
        # Retrieve the most recent command
        recent = manager.get_recent_commands(limit=1)
        
        # Verify the command was persisted with all required fields
        assert len(recent) == 1, "Command should be persisted to database"
        
        entry = recent[0]
        
        # Verify all fields are persisted correctly
        assert entry.natural_language == natural_language, "Natural language should be persisted"
        assert entry.shell_command == shell_command, "Shell command should be persisted"
        assert entry.exit_code == exit_code, "Exit code should be persisted"
        assert entry.execution_time == execution_time, "Execution time should be persisted"
        assert entry.working_directory == working_directory, "Working directory should be persisted"
        
        # Verify timestamp is present and recent (within last minute)
        assert entry.timestamp is not None, "Timestamp should be persisted"
        assert isinstance(entry.timestamp, datetime), "Timestamp should be a datetime object"
        time_diff = (datetime.now() - entry.timestamp).total_seconds()
        assert time_diff < 60, "Timestamp should be recent"
        
        # Verify id is assigned
        assert entry.id is not None, "ID should be assigned"
        assert entry.id > 0, "ID should be positive"
        
    finally:
        # Cleanup
        if os.path.exists(db_path):
            os.unlink(db_path)


@settings(max_examples=100)
@given(
    # Generate a base query term that will be used in commands
    query_term=st.text(alphabet=st.characters(whitelist_categories=('L',)), min_size=3, max_size=20).filter(lambda x: x.strip()),
    # Generate commands that contain the query term
    matching_commands=st.lists(
        st.tuples(
            st.text(alphabet=st.characters(blacklist_categories=('Cs', 'Cc')), min_size=1, max_size=100).filter(lambda x: x.strip()),
            st.text(alphabet=st.characters(blacklist_categories=('Cs', 'Cc')), min_size=1, max_size=100).filter(lambda x: x.strip()),
            st.integers(min_value=0, max_value=255),
            st.floats(min_value=0.001, max_value=60.0, allow_nan=False, allow_infinity=False)
        ),
        min_size=1,
        max_size=10
    ),
    # Generate commands that don't contain the query term
    non_matching_commands=st.lists(
        st.tuples(
            st.text(alphabet=st.characters(whitelist_categories=('N',)), min_size=1, max_size=100).filter(lambda x: x.strip() and not any(c.isalpha() for c in x)),
            st.text(alphabet=st.characters(blacklist_categories=('Cs', 'Cc')), min_size=1, max_size=100).filter(lambda x: x.strip()),
            st.integers(min_value=0, max_value=255),
            st.floats(min_value=0.001, max_value=60.0, allow_nan=False, allow_infinity=False)
        ),
        min_size=0,
        max_size=5
    )
)
def test_property_history_suggestions(query_term, matching_commands, non_matching_commands):
    """
    Feature: haunted-terminal-cli, Property 19: History-based suggestions
    
    Property: For any natural language input, if similar commands exist in history, 
    the system should retrieve and display relevant suggestions ranked by recency 
    and frequency.
    
    Validates: Requirements 11.3, 11.4
    """
    # Create a temporary database for this test
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    
    try:
        manager = HistoryManager(db_path=db_path)
        
        # Save matching commands (commands that contain the query term)
        for nl, shell, exit_code, exec_time in matching_commands:
            # Inject the query term into the natural language
            nl_with_term = f"{query_term} {nl}"
            manager.save_command(
                natural_language=nl_with_term,
                shell_command=shell,
                exit_code=exit_code,
                execution_time=exec_time,
                working_directory="/tmp"
            )
        
        # Save non-matching commands (commands that don't contain the query term)
        for nl, shell, exit_code, exec_time in non_matching_commands:
            manager.save_command(
                natural_language=nl,
                shell_command=shell,
                exit_code=exit_code,
                execution_time=exec_time,
                working_directory="/tmp"
            )
        
        # Retrieve suggestions using the query term
        suggestions = manager.get_suggestions(query_term, limit=20)
        
        # Property 1: All returned suggestions should contain the query term
        for suggestion in suggestions:
            assert query_term.lower() in suggestion.natural_language.lower(), \
                f"Suggestion '{suggestion.natural_language}' should contain query term '{query_term}'"
        
        # Property 2: The number of suggestions should not exceed the number of matching commands
        # (accounting for grouping by shell_command)
        unique_matching_shells = set(shell for _, shell, _, _ in matching_commands)
        assert len(suggestions) <= len(unique_matching_shells), \
            "Number of suggestions should not exceed unique matching commands"
        
        # Property 3: If there are matching commands, suggestions should be returned
        if matching_commands:
            assert len(suggestions) > 0, \
                "Suggestions should be returned when matching commands exist in history"
        
        # Property 4: Suggestions should be ordered by frequency and recency
        # We'll verify this by checking that more frequent commands appear first
        if len(matching_commands) >= 2:
            # Count how many times each shell command appears in matching_commands
            from collections import Counter
            shell_counts = Counter(shell for _, shell, _, _ in matching_commands)
            max_existing_count = max(shell_counts.values()) if shell_counts else 0
            
            # Save one command MORE times than any existing command to make it most frequent
            frequent_nl = f"{query_term} frequent command"
            frequent_shell = "echo frequent"
            for _ in range(max_existing_count + 2):
                manager.save_command(
                    natural_language=frequent_nl,
                    shell_command=frequent_shell,
                    exit_code=0,
                    execution_time=0.1,
                    working_directory="/tmp"
                )
            
            # Retrieve suggestions again
            suggestions_with_frequent = manager.get_suggestions(query_term, limit=20)
            
            # The frequent command should appear in the results
            frequent_found = any(s.shell_command == frequent_shell for s in suggestions_with_frequent)
            assert frequent_found, "Frequent command should appear in suggestions"
            
            # If there are multiple suggestions, the frequent one should be first
            if len(suggestions_with_frequent) > 1:
                assert suggestions_with_frequent[0].shell_command == frequent_shell, \
                    "Most frequent command should appear first in suggestions"
        
    finally:
        # Cleanup
        if os.path.exists(db_path):
            os.unlink(db_path)
