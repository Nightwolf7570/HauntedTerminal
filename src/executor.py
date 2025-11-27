"""
Command executor for safe shell execution.
"""

import subprocess
import time
import os
import shlex
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class ExecutionResult:
    """Represents the result of a command execution."""
    command: str
    stdout: str
    stderr: str
    exit_code: int
    execution_time: float
    timestamp: datetime


class CommandExecutor:
    """Executes shell commands safely and captures output."""
    
    def __init__(self, working_directory: Optional[str] = None):
        """
        Initialize the command executor.
        
        Args:
            working_directory: Directory to execute commands in. If None, uses current directory.
        """
        self.working_directory = working_directory or os.getcwd()
    
    def validate_syntax(self, command: str) -> bool:
        """
        Perform basic validation of command syntax.
        
        Args:
            command: The shell command to validate
            
        Returns:
            True if command appears valid, False otherwise
        """
        if not command or not command.strip():
            return False
        
        command = command.strip()
        
        # Check for obviously invalid patterns
        invalid_patterns = [
            # Unmatched quotes
            lambda c: c.count('"') % 2 != 0,
            lambda c: c.count("'") % 2 != 0,
            
            # Unmatched parentheses/brackets
            lambda c: c.count('(') != c.count(')'),
            lambda c: c.count('[') != c.count(']'),
            lambda c: c.count('{') != c.count('}'),
            
            # Invalid pipe usage
            lambda c: c.startswith('|'),
            lambda c: c.endswith('|'),
            lambda c: '||' in c.replace('||', ''),  # Check for single | not part of ||
            
            # Invalid redirection
            lambda c: c.startswith('>'),
            lambda c: c.startswith('<'),
        ]
        
        for check in invalid_patterns:
            try:
                if check(command):
                    return False
            except Exception:
                # If any check fails, consider it invalid
                return False
        
        # Try to parse with shlex (basic shell syntax check)
        try:
            # This will catch some basic syntax errors
            # Note: We don't use the result, just checking if it parses
            shlex.split(command, posix=True)
        except ValueError:
            # shlex.split raises ValueError for unclosed quotes and similar issues
            return False
        
        return True
    
    def execute(self, command: str) -> ExecutionResult:
        """
        Execute a shell command and capture its output.
        
        Args:
            command: The shell command to execute
            
        Returns:
            ExecutionResult containing stdout, stderr, exit code, and execution time
            
        Raises:
            ValueError: If command validation fails or command is empty
        """
        # Validate command is not empty
        if not command or not command.strip():
            raise ValueError("Command cannot be empty")
        
        # Validate command syntax
        if not self.validate_syntax(command):
            raise ValueError(
                f"Invalid command syntax: {command}\n"
                "  • Check for unmatched quotes or brackets\n"
                "  • Verify pipe and redirection usage"
            )
        
        timestamp = datetime.now()
        start_time = time.time()
        
        # Special handling for cd command
        if command.strip().startswith('cd '):
            return self._execute_cd(command, timestamp, start_time)
        
        try:
            # Execute command in the working directory
            # shell=True allows for complex commands with pipes, redirects, etc.
            # We capture both stdout and stderr separately
            result = subprocess.run(
                command,
                shell=True,
                cwd=self.working_directory,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout for long-running commands
            )
            
            execution_time = time.time() - start_time
            
            return ExecutionResult(
                command=command,
                stdout=result.stdout,
                stderr=result.stderr,
                exit_code=result.returncode,
                execution_time=execution_time,
                timestamp=timestamp
            )
            
        except subprocess.TimeoutExpired as e:
            # Requirement 7.3: Provide helpful context for timeout errors
            execution_time = time.time() - start_time
            stderr_msg = (
                f"Command timed out after 300 seconds\n"
                f"  • The command may be waiting for input\n"
                f"  • Try running with a shorter timeout or in the background\n"
                f"  • Command: {command}"
            )
            return ExecutionResult(
                command=command,
                stdout=e.stdout.decode() if e.stdout else "",
                stderr=stderr_msg,
                exit_code=-1,
                execution_time=execution_time,
                timestamp=timestamp
            )
        
        except PermissionError as e:
            # Requirement 7.3: Specific error for permission issues
            execution_time = time.time() - start_time
            stderr_msg = (
                f"Permission denied: {str(e)}\n"
                f"  • You may need elevated privileges (sudo)\n"
                f"  • Check file/directory permissions\n"
                f"  • Command: {command}"
            )
            return ExecutionResult(
                command=command,
                stdout="",
                stderr=stderr_msg,
                exit_code=-1,
                execution_time=execution_time,
                timestamp=timestamp
            )
        
        except FileNotFoundError as e:
            # Requirement 7.3: Specific error for missing commands/files
            execution_time = time.time() - start_time
            stderr_msg = (
                f"Command or file not found: {str(e)}\n"
                f"  • Check if the command is installed\n"
                f"  • Verify the file path is correct\n"
                f"  • Command: {command}"
            )
            return ExecutionResult(
                command=command,
                stdout="",
                stderr=stderr_msg,
                exit_code=-1,
                execution_time=execution_time,
                timestamp=timestamp
            )
        
        except OSError as e:
            # Requirement 7.3: OS-level errors
            execution_time = time.time() - start_time
            stderr_msg = (
                f"Operating system error: {str(e)}\n"
                f"  • The system could not execute the command\n"
                f"  • Check system resources and permissions\n"
                f"  • Command: {command}"
            )
            return ExecutionResult(
                command=command,
                stdout="",
                stderr=stderr_msg,
                exit_code=-1,
                execution_time=execution_time,
                timestamp=timestamp
            )
        
        except Exception as e:
            # Requirement 7.1, 7.4: Catch all other unexpected errors
            execution_time = time.time() - start_time
            stderr_msg = (
                f"Unexpected execution error: {str(e)}\n"
                f"  • An unknown error occurred\n"
                f"  • Command: {command}\n"
                f"  • Error type: {type(e).__name__}"
            )
            return ExecutionResult(
                command=command,
                stdout="",
                stderr=stderr_msg,
                exit_code=-1,
                execution_time=execution_time,
                timestamp=timestamp
            )
    
    def _execute_cd(self, command: str, timestamp: datetime, start_time: float) -> ExecutionResult:
        """
        Special handler for cd commands to actually change the working directory.
        
        Args:
            command: The cd command
            timestamp: Command start timestamp
            start_time: Command start time
            
        Returns:
            ExecutionResult for the cd operation
        """
        import shlex
        
        try:
            # Parse the cd command
            parts = shlex.split(command)
            if len(parts) < 2:
                # Just "cd" with no args - go to home directory
                target_dir = os.path.expanduser("~")
            else:
                target_dir = parts[1]
                # Expand ~ and environment variables
                target_dir = os.path.expanduser(target_dir)
                target_dir = os.path.expandvars(target_dir)
            
            # Make it absolute if relative
            if not os.path.isabs(target_dir):
                target_dir = os.path.join(self.working_directory, target_dir)
            
            # Normalize the path
            target_dir = os.path.normpath(target_dir)
            
            # Check if directory exists (case-insensitive on macOS)
            if not os.path.isdir(target_dir):
                # Try to find case-insensitive match
                parent = os.path.dirname(target_dir)
                basename = os.path.basename(target_dir)
                
                if os.path.isdir(parent):
                    try:
                        entries = os.listdir(parent)
                        for entry in entries:
                            if entry.lower() == basename.lower():
                                full_path = os.path.join(parent, entry)
                                if os.path.isdir(full_path):
                                    target_dir = full_path
                                    break
                    except OSError:
                        pass
            
            # Try to change directory
            if os.path.isdir(target_dir):
                os.chdir(target_dir)
                self.working_directory = os.getcwd()
                execution_time = time.time() - start_time
                
                return ExecutionResult(
                    command=command,
                    stdout=f"Changed directory to: {self.working_directory}",
                    stderr="",
                    exit_code=0,
                    execution_time=execution_time,
                    timestamp=timestamp
                )
            else:
                execution_time = time.time() - start_time
                return ExecutionResult(
                    command=command,
                    stdout="",
                    stderr=f"cd: no such file or directory: {target_dir}",
                    exit_code=1,
                    execution_time=execution_time,
                    timestamp=timestamp
                )
                
        except Exception as e:
            execution_time = time.time() - start_time
            return ExecutionResult(
                command=command,
                stdout="",
                stderr=f"cd: {str(e)}",
                exit_code=1,
                execution_time=execution_time,
                timestamp=timestamp
            )
    
    def get_working_directory(self) -> str:
        """
        Get the current working directory for command execution.
        
        Returns:
            Path to the current working directory
        """
        return self.working_directory
    
    def set_working_directory(self, directory: str) -> None:
        """
        Set the working directory for command execution.
        
        Args:
            directory: Path to the new working directory
            
        Raises:
            ValueError: If directory doesn't exist
        """
        if not os.path.isdir(directory):
            raise ValueError(f"Directory does not exist: {directory}")
        
        self.working_directory = os.path.abspath(directory)
