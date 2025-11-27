# 50 Most Common Command Examples

This document provides detailed examples for the 50 most common natural language commands and their correct shell interpretations. These examples are used to train the Ollama model for better command generation.

## File Operations (15 commands)

### 1. List Files
**Natural:** "list all files"
**Command:** `ls -la`
**Notes:** Use -la for detailed listing with hidden files

### 2. Find Files by Name
**Natural:** "find all python files"
**Command:** `find . -name "*.py" 2>/dev/null`
**Notes:** Always suppress stderr with 2>/dev/null

### 3. Find Files by Time (Recent)
**Natural:** "show me files I edited this week"
**Command:** `find . -type f -mtime -7 2>/dev/null`
**Notes:** -mtime -7 means last 7 days, NOT -mtime 7-14

### 4. Find Files by Time + Type
**Natural:** "show me python files I edited today"
**Command:** `find . -type f -name "*.py" -mtime 0 2>/dev/null`
**Notes:** Combine with AND (implicit), NEVER use -o between -name and -mtime

### 5. Find Large Files
**Natural:** "find files larger than 100MB"
**Command:** `find . -type f -size +100M 2>/dev/null`
**Notes:** Use +100M for "larger than", -100M for "smaller than"

### 6. Show Disk Usage
**Natural:** "show disk usage"
**Command:** `df -h`
**Notes:** -h for human-readable sizes

### 7. Show Directory Sizes
**Natural:** "show directory sizes"
**Command:** `du -sh */ 2>/dev/null`
**Notes:** */ targets directories only

### 8. Copy Files
**Natural:** "copy all text files to backup"
**Command:** `cp *.txt backup/ 2>/dev/null`
**Notes:** Ensure destination directory exists

### 9. Move Files
**Natural:** "move all logs to archive"
**Command:** `mv *.log archive/ 2>/dev/null`
**Notes:** Use mv for both move and rename

### 10. Delete Files
**Natural:** "delete all temp files"
**Command:** `rm *.tmp`
**Notes:** Be careful with wildcards, no -f unless explicitly requested

### 11. Create Directory
**Natural:** "create a directory called test"
**Command:** `mkdir test`
**Notes:** Use mkdir -p for nested directories

### 12. Change Directory
**Natural:** "go to home directory"
**Command:** `cd ~`
**Notes:** ~ expands to home directory

### 13. Show Current Directory
**Natural:** "where am I"
**Command:** `pwd`
**Notes:** Prints working directory

### 14. Count Files
**Natural:** "how many python files are there"
**Command:** `find . -name "*.py" 2>/dev/null | wc -l`
**Notes:** Pipe to wc -l for counting

### 15. Show File Tree
**Natural:** "show directory tree"
**Command:** `tree -L 2`
**Notes:** -L limits depth, fallback to find if tree not available

## Text Processing (10 commands)

### 16. Search in Files
**Natural:** "search for error in logs"
**Command:** `grep -i "error" *.log 2>/dev/null`
**Notes:** -i for case-insensitive, -r for recursive

### 17. Search Recursively
**Natural:** "find all files containing TODO"
**Command:** `grep -r "TODO" . 2>/dev/null`
**Notes:** -r searches recursively from current directory

### 18. Count Lines
**Natural:** "count lines in readme"
**Command:** `wc -l README.md`
**Notes:** -l for lines, -w for words, -c for characters

### 19. Show First Lines
**Natural:** "show first 10 lines of file"
**Command:** `head -n 10 file.txt`
**Notes:** Default is 10 if -n not specified

### 20. Show Last Lines
**Natural:** "show last 20 lines of log"
**Command:** `tail -n 20 app.log`
**Notes:** Use tail -f for following live updates

### 21. Sort Lines
**Natural:** "sort lines in file"
**Command:** `sort file.txt`
**Notes:** Use -r for reverse, -n for numeric sort

### 22. Remove Duplicates
**Natural:** "remove duplicate lines"
**Command:** `sort file.txt | uniq`
**Notes:** Must sort first, uniq only removes adjacent duplicates

### 23. Replace Text
**Natural:** "replace old with new in file"
**Command:** `sed -i '' 's/old/new/g' file.txt`
**Notes:** -i '' for in-place on macOS, use -i on Linux

### 24. Count Occurrences
**Natural:** "count how many times error appears"
**Command:** `grep -c "error" file.txt`
**Notes:** -c counts matching lines

### 25. Extract Column
**Natural:** "show first column of csv"
**Command:** `cut -d',' -f1 data.csv`
**Notes:** -d sets delimiter, -f selects field

## Process Management (8 commands)

### 26. Show All Processes
**Natural:** "show all running processes"
**Command:** `ps aux`
**Notes:** aux shows all processes with details

### 27. Find Process
**Natural:** "find python processes"
**Command:** `ps aux | grep python`
**Notes:** Pipe to grep for filtering

### 28. Kill Process by PID
**Natural:** "kill process 1234"
**Command:** `kill 1234`
**Notes:** Use kill -9 only if explicitly requested (force kill)

### 29. Kill Process by Name
**Natural:** "kill all python processes"
**Command:** `pkill python`
**Notes:** pkill matches by name, be careful with wildcards

### 30. Show Top Processes
**Natural:** "show top cpu consuming processes"
**Command:** `top -o cpu -n 10`
**Notes:** -o sorts by column, -n limits output

### 31. Show Memory Usage
**Natural:** "show memory usage"
**Command:** `top -l 1 -s 0 | grep PhysMem`
**Notes:** macOS specific, use free -h on Linux

### 32. Background Job
**Natural:** "run command in background"
**Command:** `command &`
**Notes:** & sends to background

### 33. List Jobs
**Natural:** "show background jobs"
**Command:** `jobs`
**Notes:** Shows jobs in current shell

## Network Operations (7 commands)

### 34. Download File
**Natural:** "download file from url"
**Command:** `curl -O https://example.com/file.zip`
**Notes:** -O saves with original filename

### 35. Fetch URL Content
**Natural:** "get content from url"
**Command:** `curl -s https://example.com`
**Notes:** -s for silent mode (no progress bar)

### 36. Download with Wget
**Natural:** "download with wget"
**Command:** `wget https://example.com/file.tar.gz`
**Notes:** wget auto-saves, curl needs -O

### 37. Ping Host
**Natural:** "ping google"
**Command:** `ping -c 4 google.com`
**Notes:** -c limits count (important on macOS, infinite by default)

### 38. Check Port
**Natural:** "check if port 8080 is open"
**Command:** `lsof -i :8080`
**Notes:** Shows what's using the port

### 39. Show Network Connections
**Natural:** "show network connections"
**Command:** `netstat -an | grep ESTABLISHED`
**Notes:** Filter by state for clarity

### 40. Test API Endpoint
**Natural:** "test api endpoint"
**Command:** `curl -X GET https://api.example.com/data`
**Notes:** -X specifies HTTP method

## macOS Specific (5 commands)

### 41. Open in Finder
**Natural:** "open current folder in finder"
**Command:** `open .`
**Notes:** . is current directory

### 42. Open Application
**Natural:** "open chrome"
**Command:** `open -a "Google Chrome"`
**Notes:** -a specifies application, use full name

### 43. Open File
**Natural:** "open readme file"
**Command:** `open README.md`
**Notes:** Opens with default application

### 44. Show Hidden Files
**Natural:** "show hidden files in finder"
**Command:** `defaults write com.apple.finder AppleShowAllFiles YES && killall Finder`
**Notes:** Requires Finder restart

### 45. Take Screenshot
**Natural:** "take screenshot"
**Command:** `screencapture -i screenshot.png`
**Notes:** -i for interactive selection

## Git Operations (5 commands)

### 46. Git Status
**Natural:** "show git status"
**Command:** `git status`
**Notes:** Shows working tree status

### 47. Git Log
**Natural:** "show recent commits"
**Command:** `git log --oneline -10`
**Notes:** --oneline for compact view, -10 limits to 10

### 48. Git Diff
**Natural:** "show changes"
**Command:** `git diff`
**Notes:** Shows unstaged changes

### 49. Git Add All
**Natural:** "stage all changes"
**Command:** `git add .`
**Notes:** . adds all files in current directory

### 50. Git Commit
**Natural:** "commit changes"
**Command:** `git commit -m "commit message"`
**Notes:** -m for inline message

## Common Patterns to Remember

### Time-Based Searches
- `-mtime -7` = last 7 days (CORRECT)
- `-mtime +7` = more than 7 days ago
- `-mtime 7` = exactly 7 days ago
- NEVER use `-mtime 7-14` (INVALID)

### Combining Conditions
- Use AND (implicit): `find . -name "*.py" -mtime -7`
- AVOID OR with different types: `find . \( -name "*.py" -o -mtime -7 \)` is WRONG

### Error Suppression
- Add `2>/dev/null` to find/grep commands
- Prevents permission denied errors from cluttering output

### File Patterns
- `*.py` = all Python files
- `*.{js,ts}` = all JavaScript and TypeScript files
- `**/test_*.py` = test files in any subdirectory

### Pipes and Chaining
- `|` pipes output to next command
- `&&` runs next command only if previous succeeds
- `;` runs commands sequentially regardless of success
