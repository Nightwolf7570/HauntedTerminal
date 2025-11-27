"""
History manager for persisting and retrieving command history using SQLite.
"""

import sqlite3
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Optional
import os


@dataclass
class HistoryEntry:
    """Represents a command history entry."""
    id: int
    natural_language: str
    shell_command: str
    working_directory: str
    exit_code: int
    timestamp: datetime
    execution_time: float


class HistoryManager:
    """Manages command history persistence and retrieval using SQLite."""
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize the history manager.
        
        Args:
            db_path: Path to SQLite database file. If None, uses default location.
        """
        if db_path is None:
            # Use default location in user's home directory
            home = Path.home()
            haunted_dir = home / ".haunted"
            haunted_dir.mkdir(exist_ok=True)
            db_path = str(haunted_dir / "history.db")
        
        self.db_path = db_path
        self.initialize_db()
    
    def initialize_db(self) -> None:
        """
        Create database schema if it doesn't exist.
        
        Raises:
            sqlite3.Error: If database initialization fails
        """
        try:
            conn = sqlite3.connect(self.db_path)
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS command_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        natural_language TEXT NOT NULL,
                        shell_command TEXT NOT NULL,
                        working_directory TEXT NOT NULL,
                        exit_code INTEGER NOT NULL,
                        timestamp DATETIME NOT NULL,
                        execution_time REAL NOT NULL
                    )
                """)
                
                # Create index for faster similarity searches
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_natural_language 
                    ON command_history(natural_language)
                """)
                
                # Create index for timestamp-based queries
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_timestamp 
                    ON command_history(timestamp DESC)
                """)
                
                # Create aliases table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS aliases (
                        name TEXT PRIMARY KEY,
                        command TEXT NOT NULL,
                        created_at DATETIME NOT NULL
                    )
                """)

                # Create rituals table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS rituals (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT UNIQUE NOT NULL,
                        description TEXT,
                        created_at DATETIME NOT NULL
                    )
                """)

                # Create ritual_steps table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS ritual_steps (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        ritual_id INTEGER NOT NULL,
                        sequence_order INTEGER NOT NULL,
                        command TEXT NOT NULL,
                        FOREIGN KEY(ritual_id) REFERENCES rituals(id) ON DELETE CASCADE
                    )
                """)

                # Create preferences table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS preferences (
                        key TEXT PRIMARY KEY,
                        value TEXT NOT NULL
                    )
                """)

                # Create rejected_commands table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS rejected_commands (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        natural_language TEXT NOT NULL,
                        shell_command TEXT NOT NULL,
                        timestamp DATETIME NOT NULL
                    )
                """)
                
                conn.commit()
            finally:
                conn.close()
        except sqlite3.Error as e:
            # Re-raise with more context for graceful degradation
            raise sqlite3.Error(f"Failed to initialize database at {self.db_path}: {str(e)}") from e
        except Exception as e:
            # Catch other unexpected errors
            raise RuntimeError(f"Unexpected error initializing database: {str(e)}") from e

    def add_rejection(self, natural_language: str, shell_command: str) -> None:
        """Record a rejected command interpretation."""
        timestamp = datetime.now().isoformat()
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO rejected_commands (natural_language, shell_command, timestamp)
                    VALUES (?, ?, ?)
                """, (natural_language, shell_command, timestamp))
        except sqlite3.Error as e:
            raise sqlite3.Error(f"Failed to record rejection: {e}")

    def get_rejections(self, natural_language: str, limit: int = 5) -> List[str]:
        """Retrieve rejected shell commands for similar natural language input."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT shell_command
                    FROM rejected_commands
                    WHERE natural_language LIKE ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                """, (f"%{natural_language}%", limit))
                return [row[0] for row in cursor.fetchall()]
        except sqlite3.Error:
            return []
    
    def clear_rejections(self, natural_language: str) -> None:
        """Clear rejected commands for a specific natural language input after success."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    DELETE FROM rejected_commands
                    WHERE natural_language = ?
                """, (natural_language,))
        except sqlite3.Error:
            pass  # Fail silently

    def set_preference(self, key: str, value: str) -> None:
        """Set a user preference."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    "INSERT OR REPLACE INTO preferences (key, value) VALUES (?, ?)",
                    (key, value)
                )
        except sqlite3.Error as e:
            raise sqlite3.Error(f"Failed to set preference: {e}")

    def get_preference(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Get a user preference."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("SELECT value FROM preferences WHERE key = ?", (key,))
                row = cursor.fetchone()
                return row[0] if row else default
        except sqlite3.Error:
            return default

    def save_command(
        self,
        natural_language: str,
        shell_command: str,
        exit_code: int,
        execution_time: float,
        working_directory: Optional[str] = None
    ) -> None:
        """
        Persist a successfully executed command to the database.
        
        Args:
            natural_language: The original natural language input
            shell_command: The interpreted shell command
            exit_code: The command's exit code
            execution_time: Time taken to execute the command in seconds
            working_directory: Directory where command was executed. If None, uses current directory.
            
        Raises:
            sqlite3.Error: If database operation fails
            ValueError: If required parameters are invalid
        """
        # Validate inputs
        if not natural_language or not natural_language.strip():
            raise ValueError("natural_language cannot be empty")
        if not shell_command or not shell_command.strip():
            raise ValueError("shell_command cannot be empty")
        if execution_time < 0:
            raise ValueError("execution_time cannot be negative")
        
        if working_directory is None:
            working_directory = os.getcwd()
        
        timestamp = datetime.now().isoformat()
        
        try:
            conn = sqlite3.connect(self.db_path)
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO command_history 
                    (natural_language, shell_command, working_directory, exit_code, timestamp, execution_time)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (natural_language, shell_command, working_directory, exit_code, timestamp, execution_time))
                conn.commit()
            finally:
                conn.close()
        except sqlite3.Error as e:
            # Re-raise with context for graceful degradation
            raise sqlite3.Error(f"Failed to save command to history: {str(e)}") from e
        except Exception as e:
            # Catch other unexpected errors
            raise RuntimeError(f"Unexpected error saving command: {str(e)}") from e
    
    def get_suggestions(self, natural_language: str, limit: int = 5) -> List[HistoryEntry]:
        """
        Retrieve similar past commands based on natural language input.
        
        Uses simple substring matching to find commands with similar natural language.
        Results are ordered by recency and frequency.
        
        Args:
            natural_language: The natural language input to match against
            limit: Maximum number of suggestions to return
            
        Returns:
            List of HistoryEntry objects matching the input
            
        Raises:
            sqlite3.Error: If database query fails
            ValueError: If parameters are invalid
        """
        if not natural_language or not natural_language.strip():
            raise ValueError("natural_language cannot be empty")
        if limit <= 0:
            raise ValueError("limit must be positive")
        
        try:
            conn = sqlite3.connect(self.db_path)
            try:
                cursor = conn.cursor()
                
                # Search for commands with similar natural language using LIKE
                # Order by frequency (count) and recency (max timestamp)
                cursor.execute("""
                    SELECT 
                        id,
                        natural_language,
                        shell_command,
                        working_directory,
                        exit_code,
                        timestamp,
                        execution_time,
                        COUNT(*) as frequency,
                        MAX(timestamp) as last_used
                    FROM command_history
                    WHERE natural_language LIKE ?
                    GROUP BY shell_command
                    ORDER BY frequency DESC, last_used DESC
                    LIMIT ?
                """, (f"%{natural_language}%", limit))
                
                rows = cursor.fetchall()
                return [
                    HistoryEntry(
                        id=row[0],
                        natural_language=row[1],
                        shell_command=row[2],
                        working_directory=row[3],
                        exit_code=row[4],
                        timestamp=datetime.fromisoformat(row[5]),
                        execution_time=row[6]
                    )
                    for row in rows
                ]
            finally:
                conn.close()
        except sqlite3.Error as e:
            # Re-raise with context
            raise sqlite3.Error(f"Failed to retrieve suggestions: {str(e)}") from e
        except Exception as e:
            # Catch other unexpected errors
            raise RuntimeError(f"Unexpected error retrieving suggestions: {str(e)}") from e
    
    def get_recent_commands(self, limit: int = 10) -> List[HistoryEntry]:
        """
        Retrieve the most recent commands from history.
        
        Args:
            limit: Maximum number of commands to return
            
        Returns:
            List of HistoryEntry objects ordered by timestamp (most recent first)
            
        Raises:
            sqlite3.Error: If database query fails
            ValueError: If limit is invalid
        """
        if limit <= 0:
            raise ValueError("limit must be positive")
        
        try:
            conn = sqlite3.connect(self.db_path)
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT 
                        id,
                        natural_language,
                        shell_command,
                        working_directory,
                        exit_code,
                        timestamp,
                        execution_time
                    FROM command_history
                    ORDER BY timestamp DESC
                    LIMIT ?
                """, (limit,))
                
                rows = cursor.fetchall()
                return [
                    HistoryEntry(
                        id=row[0],
                        natural_language=row[1],
                        shell_command=row[2],
                        working_directory=row[3],
                        exit_code=row[4],
                        timestamp=datetime.fromisoformat(row[5]),
                        execution_time=row[6]
                    )
                    for row in rows
                ]
            finally:
                conn.close()
        except sqlite3.Error as e:
            # Re-raise with context
            raise sqlite3.Error(f"Failed to retrieve recent commands: {str(e)}") from e
        except Exception as e:
            # Catch other unexpected errors
            raise RuntimeError(f"Unexpected error retrieving recent commands: {str(e)}") from e

    def get_directory_suggestions(self, directory: str, limit: int = 5) -> List[HistoryEntry]:
        """
        Retrieve frequent commands executed in the specified directory.
        """
        if limit <= 0:
            raise ValueError("limit must be positive")
            
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT 
                        id,
                        natural_language,
                        shell_command,
                        working_directory,
                        exit_code,
                        timestamp,
                        execution_time,
                        COUNT(*) as frequency,
                        MAX(timestamp) as last_used
                    FROM command_history
                    WHERE working_directory = ?
                    GROUP BY shell_command
                    ORDER BY frequency DESC, last_used DESC
                    LIMIT ?
                """, (directory, limit))
                
                rows = cursor.fetchall()
                return [
                    HistoryEntry(
                        id=row[0],
                        natural_language=row[1],
                        shell_command=row[2],
                        working_directory=row[3],
                        exit_code=row[4],
                        timestamp=datetime.fromisoformat(row[5]),
                        execution_time=row[6]
                    )
                    for row in rows
                ]
        except sqlite3.Error as e:
            raise sqlite3.Error(f"Failed to retrieve directory suggestions: {e}")

    def add_alias(self, name: str, command: str) -> None:
        """Add or update an alias."""
        if not name or not command:
            raise ValueError("Name and command are required")
            
        timestamp = datetime.now().isoformat()
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO aliases (name, command, created_at)
                    VALUES (?, ?, ?)
                """, (name, command, timestamp))
        except sqlite3.Error as e:
            raise sqlite3.Error(f"Failed to save alias: {e}")

    def get_alias(self, name: str) -> Optional[str]:
        """Get command for an alias."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("SELECT command FROM aliases WHERE name = ?", (name,))
                row = cursor.fetchone()
                return row[0] if row else None
        except sqlite3.Error:
            return None

    def remove_alias(self, name: str) -> bool:
        """Remove an alias. Returns True if removed, False if not found."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("DELETE FROM aliases WHERE name = ?", (name,))
                return cursor.rowcount > 0
        except sqlite3.Error:
            return False

    def list_aliases(self) -> List[tuple[str, str]]:
        """List all aliases. Returns list of (name, command) tuples."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("SELECT name, command FROM aliases ORDER BY name")
                return cursor.fetchall()
        except sqlite3.Error:
            return []
