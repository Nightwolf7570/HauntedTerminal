
import pytest
from src.history import HistoryManager

@pytest.fixture
def history_manager(tmp_path):
    db_path = tmp_path / "test_learning.db"
    return HistoryManager(db_path=str(db_path))

def test_rejection_flow(history_manager):
    # Record a rejection
    nl = "list my files"
    bad_cmd = "rm -rf *"
    
    history_manager.add_rejection(nl, bad_cmd)
    
    # Verify it's retrieved
    rejections = history_manager.get_rejections(nl)
    assert len(rejections) == 1
    assert rejections[0] == bad_cmd

def test_rejection_search(history_manager):
    history_manager.add_rejection("show processes", "ps aux")
    history_manager.add_rejection("show procs", "top")
    
    # Search should find "show processes"
    results = history_manager.get_rejections("show")
    assert len(results) == 2
    assert "ps aux" in results
    assert "top" in results

def test_positive_learning_retrieval(history_manager):
    # Save a good command
    history_manager.save_command("list files", "ls -la", 0, 0.1, working_directory="/tmp")
    
    # Retrieve suggestions
    suggestions = history_manager.get_suggestions("list files")
    assert len(suggestions) > 0
    assert suggestions[0].shell_command == "ls -la"
