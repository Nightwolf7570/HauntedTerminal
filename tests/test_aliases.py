
import pytest
import os
import sqlite3
from src.history import HistoryManager

@pytest.fixture
def history_manager(tmp_path):
    db_path = tmp_path / "test_history.db"
    return HistoryManager(db_path=str(db_path))

def test_add_and_get_alias(history_manager):
    history_manager.add_alias("up", "cd ..")
    assert history_manager.get_alias("up") == "cd .."

def test_update_alias(history_manager):
    history_manager.add_alias("test", "echo 1")
    history_manager.add_alias("test", "echo 2")
    assert history_manager.get_alias("test") == "echo 2"

def test_remove_alias(history_manager):
    history_manager.add_alias("del", "rm file")
    assert history_manager.remove_alias("del") is True
    assert history_manager.get_alias("del") is None
    assert history_manager.remove_alias("del") is False

def test_list_aliases(history_manager):
    history_manager.add_alias("a", "cmd_a")
    history_manager.add_alias("b", "cmd_b")
    aliases = history_manager.list_aliases()
    assert len(aliases) == 2
    assert ("a", "cmd_a") in aliases
    assert ("b", "cmd_b") in aliases

def test_alias_persistence(tmp_path):
    db_path = tmp_path / "test_persist.db"
    hm1 = HistoryManager(db_path=str(db_path))
    hm1.add_alias("p", "persist")
    
    hm2 = HistoryManager(db_path=str(db_path))
    assert hm2.get_alias("p") == "persist"
