
import pytest
import sqlite3
from src.rituals import RitualManager, Ritual, RitualStep

@pytest.fixture
def ritual_manager(tmp_path):
    db_path = tmp_path / "test_rituals.db"
    
    # Initialize DB schema manually for test since HistoryManager does it in app
    with sqlite3.connect(str(db_path)) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS rituals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                description TEXT,
                created_at DATETIME NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS ritual_steps (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ritual_id INTEGER NOT NULL,
                sequence_order INTEGER NOT NULL,
                command TEXT NOT NULL,
                FOREIGN KEY(ritual_id) REFERENCES rituals(id) ON DELETE CASCADE
            )
        """)
        
    return RitualManager(db_path=str(db_path))

def test_create_and_get_ritual(ritual_manager):
    ritual_manager.create_ritual(
        name="deploy",
        description="Deploy to prod",
        steps=["git pull", "npm install", "npm run build"]
    )
    
    r = ritual_manager.get_ritual("deploy")
    assert r is not None
    assert r.name == "deploy"
    assert r.description == "Deploy to prod"
    assert len(r.steps) == 3
    assert r.steps[0].command == "git pull"
    assert r.steps[1].command == "npm install"

def test_list_rituals(ritual_manager):
    ritual_manager.create_ritual("r1", "d1", ["c1"])
    ritual_manager.create_ritual("r2", "d2", ["c2"])
    
    rituals = ritual_manager.list_rituals()
    assert len(rituals) == 2
    names = {r.name for r in rituals}
    assert "r1" in names
    assert "r2" in names

def test_delete_ritual(ritual_manager):
    ritual_manager.create_ritual("temp", "desc", ["cmd"])
    assert ritual_manager.delete_ritual("temp") is True
    assert ritual_manager.get_ritual("temp") is None
    assert ritual_manager.delete_ritual("temp") is False

def test_duplicate_ritual_name(ritual_manager):
    ritual_manager.create_ritual("dup", "desc", ["cmd"])
    with pytest.raises(ValueError):
        ritual_manager.create_ritual("dup", "desc2", ["cmd2"])
