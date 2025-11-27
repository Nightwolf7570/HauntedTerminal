"""
Ollama client for natural language to shell command interpretation.
"""

import requests
from typing import Optional
from dataclasses import dataclass


@dataclass
class OllamaConfig:
    """Configuration for Ollama client."""
    endpoint: str = "http://localhost:11434"
    model: str = "llama3.2"
    timeout: int = 10


class OllamaConnectionError(Exception):
    """Raised when connection to Ollama fails."""
    pass


class OllamaInterpretationError(Exception):
    """Raised when Ollama cannot interpret the command."""
    pass


class OllamaClient:
    """Client for interacting with local Ollama service."""
    
    def __init__(self, config: Optional[OllamaConfig] = None):
        """
        Initialize Ollama client.
        
        Args:
            config: Optional configuration. Uses defaults if not provided.
        """
        self.config = config or OllamaConfig()
    
    def check_connection(self) -> bool:
        """
        Verify that Ollama service is running and accessible.
        
        Returns:
            True if Ollama is available, False otherwise.
        
        Raises:
            OllamaConnectionError: If connection check fails with details.
        """
        try:
            response = requests.get(
                f"{self.config.endpoint}/api/tags",
                timeout=self.config.timeout
            )
            response.raise_for_status()
            return True
        except requests.exceptions.ConnectionError as e:
            raise OllamaConnectionError(
                f"Cannot connect to Ollama at {self.config.endpoint}. "
                "Is Ollama running? Try: 'ollama serve'"
            ) from e
        except requests.exceptions.Timeout as e:
            raise OllamaConnectionError(
                f"Connection to Ollama timed out after {self.config.timeout} seconds."
            ) from e
        except requests.exceptions.RequestException as e:
            raise OllamaConnectionError(
                f"Error connecting to Ollama: {str(e)}"
            ) from e
    
    def _categorize_domain(self, user_input: str) -> list[str]:
        """
        Categorize user input into command domains.
        
        Args:
            user_input: Natural language input from user.
        
        Returns:
            List of detected domain categories (file, process, network, text).
        """
        input_lower = user_input.lower()
        domains = []
        
        # File operation keywords
        file_keywords = [
            'find', 'search', 'locate', 'list', 'ls', 'copy', 'cp', 'move', 'mv',
            'rename', 'delete', 'remove', 'file', 'files', 'directory', 'folder',
            'path', 'tree', 'disk', 'space', 'size', 'du', 'df'
        ]
        if any(keyword in input_lower for keyword in file_keywords):
            domains.append('file')
        
        # Process management keywords
        process_keywords = [
            'process', 'kill', 'stop', 'terminate', 'ps', 'top', 'running',
            'background', 'foreground', 'job', 'jobs', 'bg', 'fg', 'cpu', 'memory',
            'ram', 'performance', 'monitor'
        ]
        if any(keyword in input_lower for keyword in process_keywords):
            domains.append('process')
        
        # Network operation keywords
        network_keywords = [
            'download', 'upload', 'curl', 'wget', 'fetch', 'http', 'https',
            'ping', 'network', 'connection', 'port', 'netstat', 'ip', 'dns',
            'url', 'api', 'request'
        ]
        if any(keyword in input_lower for keyword in network_keywords):
            domains.append('network')
        
        # Text processing keywords
        text_keywords = [
            'grep', 'search', 'filter', 'sed', 'awk', 'replace', 'substitute',
            'cut', 'sort', 'uniq', 'unique', 'count', 'wc', 'lines', 'words',
            'pattern', 'match', 'pipe', 'extract'
        ]
        if any(keyword in input_lower for keyword in text_keywords):
            domains.append('text')
        
        return domains
    
    def _get_comprehensive_examples(self) -> str:
        """
        Get comprehensive examples covering the 50 most common commands.
        
        Returns:
            String containing comprehensive command examples.
        """
        return """
COMPREHENSIVE COMMAND EXAMPLES (Follow these patterns):

FILE OPERATIONS:
User: "list all files"
Response: ls -la

User: "find all python files"
Response: find . -name "*.py" 2>/dev/null

User: "show me files I edited this week"
Response: find . -type f -mtime -7 2>/dev/null

User: "show me python files I edited today"
Response: find . -type f -name "*.py" -mtime 0 2>/dev/null

User: "find files larger than 100MB"
Response: find . -type f -size +100M 2>/dev/null

User: "show disk usage"
Response: df -h

User: "show directory sizes"
Response: du -sh */ 2>/dev/null

User: "copy all text files to backup"
Response: cp *.txt backup/ 2>/dev/null

User: "move all logs to archive"
Response: mv *.log archive/ 2>/dev/null

User: "create a directory called test"
Response: mkdir test

User: "go to home directory"
Response: cd ~

User: "where am I"
Response: pwd

User: "how many python files are there"
Response: find . -name "*.py" 2>/dev/null | wc -l

TEXT PROCESSING:
User: "search for error in logs"
Response: grep -i "error" *.log 2>/dev/null

User: "find all files containing TODO"
Response: grep -r "TODO" . 2>/dev/null

User: "count lines in readme"
Response: wc -l README.md

User: "show first 10 lines of file"
Response: head -n 10 file.txt

User: "show last 20 lines of log"
Response: tail -n 20 app.log

User: "sort lines in file"
Response: sort file.txt

User: "remove duplicate lines"
Response: sort file.txt | uniq

User: "replace old with new in file"
Response: sed -i '' 's/old/new/g' file.txt

User: "count how many times error appears"
Response: grep -c "error" file.txt

PROCESS MANAGEMENT:
User: "show all running processes"
Response: ps aux

User: "find python processes"
Response: ps aux | grep python

User: "kill process 1234"
Response: kill 1234

User: "show top cpu consuming processes"
Response: top -o cpu -n 10

User: "show background jobs"
Response: jobs

NETWORK OPERATIONS:
User: "download file from url"
Response: curl -O https://example.com/file.zip

User: "get content from url"
Response: curl -s https://example.com

User: "ping google"
Response: ping -c 4 google.com

User: "check if port 8080 is open"
Response: lsof -i :8080

User: "test api endpoint"
Response: curl -X GET https://api.example.com/data

MACOS SPECIFIC:
User: "open current folder in finder"
Response: open .

User: "open chrome"
Response: open -a "Google Chrome"

User: "open readme file"
Response: open README.md

GIT OPERATIONS:
User: "show git status"
Response: git status

User: "show recent commits"
Response: git log --oneline -10

User: "show changes"
Response: git diff

User: "stage all changes"
Response: git add .
"""
    
    def _get_domain_examples(self, user_input: str) -> str:
        """
        Get domain-specific examples based on user input categorization.
        
        Args:
            user_input: Natural language input from user.
        
        Returns:
            String containing relevant domain-specific examples.
        """
        domains = self._categorize_domain(user_input)
        
        if not domains:
            # Return general examples if no specific domain detected
            return """
Examples:
User: "show disk usage"
Response: df -h

User: "create a directory called test"
Response: mkdir test

User: "open current folder in finder"
Response: open .
"""
        
        examples = "\nExamples:"
        
        # File operations examples
        if 'file' in domains:
            examples += """

File Operations:
User: "list all python files"
Response: find . -name "*.py" 2>/dev/null

User: "find all pdf files in my home directory"
Response: find ~ -name "*.pdf" 2>/dev/null

User: "find files larger than 100MB"
Response: find . -type f -size +100M 2>/dev/null

User: "find files modified in the last 7 days"
Response: find . -type f -mtime -7 2>/dev/null

User: "find python files modified in the last week"
Response: find . -type f -name "*.py" -mtime -7 2>/dev/null

User: "find files modified more than 30 days ago"
Response: find . -type f -mtime +30 2>/dev/null

User: "find files modified today"
Response: find . -type f -mtime 0 2>/dev/null

User: "show me python files I edited this week"
Response: find . -type f -name "*.py" -mtime -7 2>/dev/null

User: "find javascript files modified in last 3 days"
Response: find . -type f -name "*.js" -mtime -3 2>/dev/null

User: "copy all text files to backup folder"
Response: cp *.txt backup/ 2>/dev/null

User: "move old logs to archive"
Response: mv *.log archive/ 2>/dev/null

User: "show directory sizes"
Response: du -sh */ 2>/dev/null
"""
        
        # Process management examples
        if 'process' in domains:
            examples += """

Process Management:
User: "show all running processes"
Response: ps aux

User: "find python processes"
Response: ps aux | grep python

User: "kill process 1234"
Response: kill 1234

User: "show top cpu consuming processes"
Response: top -o cpu -n 10

User: "list background jobs"
Response: jobs

User: "bring job 1 to foreground"
Response: fg %1

User: "send process to background"
Response: bg %1
"""
        
        # Network operations examples
        if 'network' in domains:
            examples += """

Network Operations:
User: "download file from url"
Response: curl -O https://example.com/file.zip

User: "fetch webpage content"
Response: curl -s https://example.com

User: "download with wget"
Response: wget https://example.com/file.tar.gz

User: "ping google"
Response: ping -c 4 google.com

User: "check open ports"
Response: netstat -an | grep LISTEN

User: "test api endpoint"
Response: curl -X GET https://api.example.com/data
"""
        
        # Text processing examples
        if 'text' in domains:
            examples += """

Text Processing:
User: "search for error in logs"
Response: grep -i "error" *.log 2>/dev/null

User: "find lines containing pattern"
Response: grep -r "pattern" . 2>/dev/null

User: "replace text in file"
Response: sed -i '' 's/old/new/g' file.txt

User: "count lines in file"
Response: wc -l file.txt

User: "sort and remove duplicates"
Response: sort file.txt | uniq

User: "extract first column"
Response: cut -d',' -f1 data.csv

User: "find unique values"
Response: cat file.txt | sort | uniq -c | sort -rn

User: "search and count occurrences"
Response: grep -c "pattern" file.txt
"""
        
        return examples
    
    def build_prompt(
        self, 
        user_input: str, 
        context: str = "", 
        history: list[tuple[str, str]] = None,
        rejections: list[str] = None,
        blacklist: list[str] = None
    ) -> str:
        """
        Construct system prompt for command interpretation with domain-specific examples.
        
        Args:
            user_input: Natural language command from user.
            context: Optional context about the environment/project.
            history: List of (natural_language, shell_command) tuples (successful past commands).
            rejections: List of shell commands to avoid.
            blacklist: List of patterns that must NEVER appear in commands.
        
        Returns:
            Formatted prompt for Ollama.
        """
        system_prompt = """You are a shell command interpreter. Convert natural language descriptions into shell commands.

Rules:
- Return ONLY the shell command, nothing else
- No explanations, no markdown, no code blocks
- Use standard bash/zsh syntax for macOS
- Be precise and safe
- If the request is unclear, return the closest safe interpretation
- Use the file list in the Context to correct file name casing (e.g., if User asks for 'readme.md' but Context shows 'README.md', use 'README.md')
- For find/grep commands that may hit permission errors, add '2>/dev/null' to suppress error messages
- When searching home directory or system paths, always suppress stderr with '2>/dev/null'
- Prefer safe, non-destructive operations when ambiguous
- Use proper quoting for filenames with spaces or special characters
- On macOS, use 'open' command to launch applications: 'open -a "App Name"'
- On macOS, use 'open' command to open files with default application: 'open filename'
- On macOS, use 'open .' to open current directory in Finder
- For complex operations, use pipes and command chaining appropriately

IMPORTANT - Time-based file searches:
- Use -mtime with a SINGLE number, not a range
- -mtime -7 means "modified in the last 7 days" (less than 7 days ago)
- -mtime +7 means "modified more than 7 days ago"
- -mtime 7 means "modified exactly 7 days ago"
- NEVER use syntax like -mtime 7-14 (this is INVALID)
- When combining -name and -mtime, use AND (implicit), NEVER use -o (OR)
- CORRECT: find . -name "*.py" -mtime -7 (python files modified in last 7 days)
- WRONG: find with -o between -name and -mtime (this finds ALL python files OR all recent files)
"""
        
        # Add learned patterns from history
        if history:
            system_prompt += "\nLearned Patterns (Follow these examples):"
            for nl, cmd in history[:3]:  # Limit to 3 to save tokens
                system_prompt += f"\nUser: \"{nl}\"\nResponse: {cmd}"
        
        # Add negative constraints
        if rejections:
            system_prompt += "\n\nREJECTED COMMANDS (User rejected these - generate a COMPLETELY DIFFERENT command):"
            for cmd in rejections[:3]:
                system_prompt += f"\n- REJECTED: {cmd}"
            system_prompt += "\nIMPORTANT: Do NOT generate the same or similar command. Try a different approach!"
        
        # Add blacklist (NEVER use these patterns)
        if blacklist:
            system_prompt += "\n\nBLACKLIST (NEVER include these patterns in ANY command):"
            for pattern in blacklist:
                system_prompt += f"\n- NEVER use: {pattern}"
        
        # Add comprehensive examples (always included for consistency)
        system_prompt += self._get_comprehensive_examples()
        
        # Add domain-specific examples for additional context
        domain_examples = self._get_domain_examples(user_input)
        if domain_examples.strip():
            system_prompt += "\n" + domain_examples
        
        system_prompt += "\n\nNow interpret this command:"
        
        context_str = f"\nContext: {context}" if context else ""
        return f"{system_prompt}{context_str}\nUser: {user_input}\nResponse:"
    
    def interpret_command(
        self, 
        natural_language: str, 
        context: str = "",
        history: list[tuple[str, str]] = None,
        rejections: list[str] = None,
        blacklist: list[str] = None
    ) -> str:
        """
        Send natural language to Ollama and get shell command interpretation.
        
        Args:
            natural_language: User's natural language command.
            context: Optional project/environment context.
            history: Learned patterns.
            rejections: Avoided interpretations.
            blacklist: Patterns that must NEVER appear.
        
        Returns:
            Interpreted shell command.
        
        Raises:
            OllamaConnectionError: If connection fails.
            OllamaInterpretationError: If interpretation fails or returns invalid result.
        """
        if not natural_language or not natural_language.strip():
            raise OllamaInterpretationError("Cannot interpret empty input")
        
        prompt = self.build_prompt(natural_language, context, history, rejections, blacklist)
        
        try:
            response = requests.post(
                f"{self.config.endpoint}/api/generate",
                json={
                    "model": self.config.model,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=self.config.timeout
            )
            response.raise_for_status()
            
            result = response.json()
            
            if "response" not in result:
                raise OllamaInterpretationError(
                    "Invalid response format from Ollama"
                )
            
            command = result["response"].strip()
            
            if not command:
                raise OllamaInterpretationError(
                    "Ollama returned empty command. Please rephrase your request."
                )
            
            # Clean up common formatting issues
            command = self._clean_command(command)
            
            return command
            
        except requests.exceptions.ConnectionError as e:
            raise OllamaConnectionError(
                f"Lost connection to Ollama at {self.config.endpoint}. "
                "Is Ollama still running?"
            ) from e
        except requests.exceptions.Timeout as e:
            raise OllamaConnectionError(
                f"Ollama request timed out after {self.config.timeout} seconds. "
                "The model may be processing a complex request."
            ) from e
        except requests.exceptions.RequestException as e:
            raise OllamaConnectionError(
                f"Error communicating with Ollama: {str(e)}"
            ) from e
        except (KeyError, ValueError) as e:
            raise OllamaInterpretationError(
                f"Failed to parse Ollama response: {str(e)}"
            ) from e
    
    def _clean_command(self, command: str) -> str:
        """
        Clean up command string from common formatting issues.
        
        Args:
            command: Raw command from Ollama.
        
        Returns:
            Cleaned command string.
        """
        # Remove markdown code blocks if present
        if command.startswith("```"):
            lines = command.split("\n")
            # Remove first line (```bash or similar)
            lines = lines[1:]
            # Remove last line if it's closing ```
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            command = "\n".join(lines).strip()
        
        # Remove inline code markers
        command = command.replace("`", "")
        
        # Remove common prefixes
        prefixes = ["$ ", "# ", "> "]
        for prefix in prefixes:
            if command.startswith(prefix):
                command = command[len(prefix):]
        
        return command.strip()

    def explain_command(self, command: str) -> str:
        """
        Ask Ollama to explain a shell command.
        
        Args:
            command: Shell command to explain.
            
        Returns:
            Explanation string.
        """
        system_prompt = """You are a helpful terminal assistant. Explain what this shell command does in plain English.
        
Rules:
- Be concise (1-2 sentences max)
- Focus on the action and the target
- Do not mention flags explicitly unless necessary for understanding
- Start with a verb (e.g., "Lists...", "Removes...", "Updates...")
"""
        prompt = f"{system_prompt}\nCommand: {command}\nExplanation:"
        
        try:
            response = requests.post(
                f"{self.config.endpoint}/api/generate",
                json={
                    "model": self.config.model,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=self.config.timeout
            )
            response.raise_for_status()
            
            result = response.json()
            
            if "response" not in result:
                return "Could not generate explanation."
            
            return result["response"].strip()
            
        except Exception:
            return "Explanation unavailable (connection error)."
