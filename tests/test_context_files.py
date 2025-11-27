
import pytest
import os
from src.context import ContextManager

@pytest.fixture
def context_manager():
    return ContextManager()

def test_get_file_list(context_manager, tmp_path):
    # Create some files in tmp_path
    (tmp_path / "file1.txt").touch()
    (tmp_path / "File2.txt").touch()
    (tmp_path / ".hidden").touch()
    
    file_list = context_manager.get_file_list(str(tmp_path))
    
    assert "file1.txt" in file_list
    assert "File2.txt" in file_list
    assert ".hidden" not in file_list # Hidden files filtered out

def test_get_file_list_limit(context_manager, tmp_path):
    # Create 10 files
    for i in range(10):
        (tmp_path / f"file{i}.txt").touch()
        
    # Limit to 5
    file_list = context_manager.get_file_list(str(tmp_path), limit=5)
    
    assert "file0.txt" in file_list
    assert "file4.txt" in file_list
    assert "more)" in file_list
    assert file_list.count(",") >= 5 # 4 commas for 5 items + ellipsis comma
