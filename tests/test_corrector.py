
import pytest
import os
from src.corrector import PathCorrector

@pytest.fixture
def corrector():
    return PathCorrector()

def test_correct_paths_case_insensitive(corrector, tmp_path):
    # Create file
    (tmp_path / "MyFile.txt").touch()
    
    # Command with wrong case
    cmd = "cat myfile.txt"
    corrected = corrector.correct_paths(cmd, str(tmp_path))
    
    assert corrected == "cat MyFile.txt"

def test_correct_paths_fuzzy(corrector, tmp_path):
    # Create file
    (tmp_path / "documentation.md").touch()
    
    # Command with typo
    cmd = "open docmntation.md"
    corrected = corrector.correct_paths(cmd, str(tmp_path))
    
    assert corrected == "open documentation.md"

def test_no_correction_if_exists(corrector, tmp_path):
    (tmp_path / "file.txt").touch()
    
    cmd = "ls file.txt"
    corrected = corrector.correct_paths(cmd, str(tmp_path))
    
    assert corrected == "ls file.txt"

def test_ignores_flags(corrector, tmp_path):
    (tmp_path / "file.txt").touch()
    
    # -l shouldn't be corrected
    cmd = "ls -l file.txt"
    corrected = corrector.correct_paths(cmd, str(tmp_path))
    
    assert corrected == "ls -l file.txt"
