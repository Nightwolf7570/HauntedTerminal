# Haunted Terminal CLI - 3-Minute Demo Script

## [0:00-0:30] Hook & Introduction
- Ever wish your terminal could just understand you?
- Not memorize aliases, not parse cryptic flags
- Meet Haunted Terminal - CLI that speaks your language
- Ghostly spirits powered by local LLMs (Ollama)
- No cloud, no API keys, fully offline
- Just you and the spirits of Unix past

## [0:30-1:15] Natural Language Commands
- Demo: "show me all python files modified in the last week"
- Spirits whisper back: `find . -name "*.py" -mtime -7`
- Shows command before executing - you stay in control
- Demo: "find large log files over 100MB and show their sizes"
- Generates find with size filters and exec flags
- Demo: "what branches haven't been merged to main?"
- Result: `git branch --no-merged main`
- Handles file operations, system queries, git workflows
- All in plain English

## [1:15-2:00] Safety System
- Critical part: this generates real shell commands
- Not a toy - could wreck your system
- Demo dangerous: "delete all files in my home directory"
- Red warnings, skull symbols, spirits grow restless
- Shows command: `rm -rf ~/*`
- Immediately BLOCKED
- Multi-layered safety checks
- Recursive deletes, system mods, privilege escalations all blocked
- Demo risky: "remove all docker containers"
- Yellow warning - requires careful consideration
- Shows exact command, asks for confirmation
- Legitimate risky operations get human in the loop
- You stay in control

## [2:00-2:45] History & Context
- Type "history" - every command logged with timestamps
- The spirits remember everything
- Demo context: "run that find command again but for javascript files"
- Recalls previous intent and adapts
- Generates: `find . -name "*.js" -mtime -7`
- Context-aware - not just translating, understanding your workflow

## [2:45-3:00] Tech Stack & Close
- Built with Python, Rich for terminal UI, Ollama for LLM inference
- Fully offline, fully open source
- Read every line of code
- Modify safety rules
- Swap out AI models
- Haunted Terminal: your shell should be smarter than your aliases
- The spirits are waiting
