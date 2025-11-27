"""
Ritual Manager for handling multi-step command workflows.
Orchestrates complex multi-command workflows with visual feedback.
"""

import sqlite3
import time
from dataclasses import dataclass
from typing import List, Optional, Callable
from datetime import datetime
from enum import Enum

class StepStatus(Enum):
    """Status of a ritual step."""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"

@dataclass
class RitualStep:
    order: int
    command: str
    description: Optional[str] = None
    status: StepStatus = StepStatus.PENDING
    output: Optional[str] = None
    error: Optional[str] = None
    execution_time: float = 0.0

@dataclass
class Ritual:
    id: int
    name: str
    description: str
    steps: List[RitualStep]
    
@dataclass
class RitualExecution:
    """Tracks the execution of a ritual."""
    ritual: Ritual
    current_step: int = 0
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    success: bool = False

class RitualManager:
    """Manages the creation, retrieval, and execution of command rituals."""
    
    def __init__(self, db_path: str):
        self.db_path = db_path

    def create_ritual(self, name: str, description: str, steps: List[str]) -> None:
        """Create a new ritual with a sequence of commands."""
        if not name or not steps:
            raise ValueError("Ritual must have a name and at least one step.")
            
        timestamp = datetime.now().isoformat()
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Insert ritual
                cursor.execute(
                    "INSERT INTO rituals (name, description, created_at) VALUES (?, ?, ?)",
                    (name, description, timestamp)
                )
                ritual_id = cursor.lastrowid
                
                # Insert steps
                for i, cmd in enumerate(steps):
                    cursor.execute(
                        "INSERT INTO ritual_steps (ritual_id, sequence_order, command) VALUES (?, ?, ?)",
                        (ritual_id, i, cmd)
                    )
        except sqlite3.IntegrityError:
            raise ValueError(f"A ritual named '{name}' already exists.")
        except sqlite3.Error as e:
            raise sqlite3.Error(f"Failed to create ritual: {e}")

    def get_ritual(self, name: str) -> Optional[Ritual]:
        """Retrieve a ritual and its steps by name."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get ritual info
                cursor.execute("SELECT id, name, description FROM rituals WHERE name = ?", (name,))
                row = cursor.fetchone()
                if not row:
                    return None
                
                ritual_id, r_name, r_desc = row
                
                # Get steps
                cursor.execute(
                    "SELECT sequence_order, command FROM ritual_steps WHERE ritual_id = ? ORDER BY sequence_order",
                    (ritual_id,)
                )
                steps = [RitualStep(order=r[0], command=r[1]) for r in cursor.fetchall()]
                
                return Ritual(id=ritual_id, name=r_name, description=r_desc, steps=steps)
        except sqlite3.Error:
            return None

    def list_rituals(self) -> List[Ritual]:
        """List all available rituals (without steps for brevity)."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, name, description FROM rituals ORDER BY name")
                return [
                    Ritual(id=r[0], name=r[1], description=r[2], steps=[]) 
                    for r in cursor.fetchall()
                ]
        except sqlite3.Error:
            return []

    def delete_ritual(self, name: str) -> bool:
        """Delete a ritual by name."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("DELETE FROM rituals WHERE name = ?", (name,))
                return cursor.rowcount > 0
        except sqlite3.Error:
            return False
    
    def execute_ritual(
        self, 
        ritual: Ritual, 
        executor_func: Callable[[str], tuple[int, str, str]],
        progress_callback: Optional[Callable[[RitualStep, int, int], None]] = None
    ) -> RitualExecution:
        """
        Execute a ritual with visual progress feedback.
        
        Args:
            ritual: The ritual to execute
            executor_func: Function that executes a command and returns (exit_code, stdout, stderr)
            progress_callback: Optional callback for progress updates
            
        Returns:
            RitualExecution with results
        """
        execution = RitualExecution(
            ritual=ritual,
            start_time=datetime.now()
        )
        
        total_steps = len(ritual.steps)
        
        for i, step in enumerate(ritual.steps):
            execution.current_step = i
            step.status = StepStatus.RUNNING
            
            # Call progress callback
            if progress_callback:
                progress_callback(step, i + 1, total_steps)
            
            # Execute the command
            start_time = time.time()
            try:
                exit_code, stdout, stderr = executor_func(step.command)
                step.execution_time = time.time() - start_time
                step.output = stdout
                step.error = stderr
                
                if exit_code == 0:
                    step.status = StepStatus.SUCCESS
                else:
                    step.status = StepStatus.FAILED
                    # Stop execution on failure
                    execution.end_time = datetime.now()
                    execution.success = False
                    return execution
                    
            except Exception as e:
                step.status = StepStatus.FAILED
                step.error = str(e)
                step.execution_time = time.time() - start_time
                execution.end_time = datetime.now()
                execution.success = False
                return execution
        
        # All steps completed successfully
        execution.end_time = datetime.now()
        execution.success = True
        return execution
