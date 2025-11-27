# 👻 Haunted Terminal

A clean, modern command-line interface that interprets natural language commands using a local LLM and executes real system operations. The application operates completely offline after initial setup and prioritizes user safety through confirmation prompts for destructive operations.

```
    ██╗  ██╗ █████╗ ██╗   ██╗███╗   ██╗████████╗███████╗██████╗ 
    ██║  ██║██╔══██╗██║   ██║████╗  ██║╚══██╔══╝██╔════╝██╔══██╗
    ███████║███████║██║   ██║██╔██╗ ██║   ██║   █████╗  ██║  ██║
    ██╔══██║██╔══██║██║   ██║██║╚██╗██║   ██║   ██╔══╝  ██║  ██║
    ██║  ██║██║  ██║╚██████╔╝██║ ╚████║   ██║   ███████╗██████╔╝
    ╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝   ╚═╝   ╚══════╝╚═════╝ 

status: ready · model: llama3.2 · v0.1.0
```

## ✨ Features

- 🗣️ **Natural Language Commands**: Type what you want in plain English
- 🤖 **Local LLM Processing**: Uses Ollama with llama3.2 for command interpretation
- 🔒 **Safety First**: Warns and confirms before destructive operations
- 🎨 **Clean, Modern Design**: Minimal interface inspired by Gemini CLI with teal and purple accents
- 📜 **Command History**: Remembers your commands across sessions with SQLite
- 🔌 **Completely Offline**: No external API calls, all processing happens locally
- ✨ **Subtle Animations**: Clean loading indicators and well-spaced output

## 📋 Requirements

### System Requirements

- **Python**: 3.10 or higher
- **Operating System**: macOS, Linux, or Windows with WSL
- **Ollama**: Local LLM service (installation instructions below)

### Python Dependencies

All Python dependencies are listed in `requirements.txt`:

- `typer>=0.9.0` - CLI framework
- `rich>=13.0.0` - Terminal styling and formatting
- `requests>=2.31.0` - HTTP client for Ollama API
- `hypothesis>=6.92.0` - Property-based testing (development)
- `pytest>=7.4.0` - Testing framework (development)

## 🚀 Installation

### Step 1: Install Ollama

Ollama is required to run the local LLM that interprets your natural language commands.

#### macOS
```bash
brew install ollama
```

#### Linux
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

#### Windows
Download the installer from [ollama.com](https://ollama.com/download)

### Step 2: Pull the llama3.2 Model

After installing Ollama, download the llama3.2 model:

```bash
ollama pull llama3.2
```

### Step 3: Start Ollama Service

Start the Ollama service (it will run in the background):

```bash
ollama serve
```

**Note**: On macOS and Windows, Ollama typically starts automatically. On Linux, you may need to start it manually or set it up as a systemd service.

### Step 4: Install Haunted Terminal

Clone the repository:

```bash
# Clone the repository
git clone <repository-url>
cd haunted-terminal-cli
```

#### ⭐ Recommended: Professional Installation (Development Mode)

This is the professional way to install CLI tools (like pip, black, pytest):

```bash
pip install -e .
```

This will:
- Install all dependencies automatically
- Create a `haunted` command available system-wide
- Allow you to edit the code and see changes immediately
- Follow Python packaging best practices

#### Alternative: Manual Installation

If you prefer to install dependencies manually:

```bash
pip install -r requirements.txt
```

**Note**: With manual installation, you'll need to run `python haunted.py` instead of just `haunted`.

## 🎮 Usage

### Starting the Application

If you installed with `pip install -e .` (recommended):

```bash
haunted
```

This works from anywhere on your system! 🎉

Alternatively, if you installed manually:

```bash
python haunted.py
```

### Example Commands

Once the application starts, you'll see a clean welcome header. Simply type what you want to do in natural language:

```
› list all python files in this directory

╭────────────────────────────────────────────────────────────╮
  you: list all python files in this directory
  ghost: find . -name "*.py"
╰────────────────────────────────────────────────────────────╯

execute? (y/n)
```

#### More Examples

```
› show me the current directory
› create a new folder called test
› find all files modified in the last 24 hours
› show disk usage for this folder
› count lines in all python files
```

### Safety Features

The Haunted Terminal protects you from destructive operations:

```
› delete all temporary files

⚠ warning: destructive operation detected

╭────────────────────────────────────────────────────────────╮
  you: delete all temporary files
  ghost: rm -rf /tmp/*
╰────────────────────────────────────────────────────────────╯

Type 'CONFIRM' to proceed, or anything else to cancel:
```

### Exiting the Application

Type `exit` or `quit` to leave the Haunted Terminal:

```
› exit

goodbye
2 commands executed this session
```

## 🔧 Troubleshooting

### "Cannot connect to Ollama"

**Problem**: The application can't reach the Ollama service.

**Solutions**:
1. Check if Ollama is running:
   ```bash
   curl http://localhost:11434/api/tags
   ```
   
2. Start Ollama if it's not running:
   ```bash
   ollama serve
   ```

3. Verify the llama3.2 model is installed:
   ```bash
   ollama list
   ```
   
4. If llama3.2 is missing, pull it:
   ```bash
   ollama pull llama3.2
   ```

### "Command interpretation timeout"

**Problem**: Ollama is taking too long to respond (>10 seconds).

**Solutions**:
1. The llama3.2 model might be loading for the first time (this is normal)
2. Try the command again - subsequent requests are usually faster
3. Check system resources - Ollama requires adequate RAM
4. Consider using a smaller model if your system is resource-constrained

### "Permission denied" errors

**Problem**: Commands fail with permission errors.

**Solutions**:
1. Some operations require sudo privileges
2. Run the specific command with sudo manually, or
3. Rephrase your request to avoid privileged operations

### Database errors

**Problem**: SQLite database errors when saving history.

**Solutions**:
1. Check write permissions in the application directory
2. Delete the database file to reset: `rm haunted_history.db`
3. The application will create a new database on next run

### Commands not executing as expected

**Problem**: The interpreted command doesn't match your intent.

**Solutions**:
1. Be more specific in your natural language request
2. Review the command preview before confirming
3. Type 'n' to cancel and rephrase your request
4. You can always type the exact shell command if needed

## ✅ Verifying Installation

To verify everything is working correctly:

### 1. Check Python Version
```bash
python --version
# Should show Python 3.10 or higher
```

### 2. Check Ollama Connection
```bash
curl http://localhost:11434/api/tags
# Should return JSON with available models
```

### 3. Verify llama3.2 Model
```bash
ollama list | grep llama3.2
# Should show llama3.2 in the list
```

### 4. Test the Application
```bash
haunted
```

Or if you didn't use `pip install -e .`:
```bash
python haunted.py
```

You should see:
- A clean, minimal header: `haunted ▸ terminal`
- System status showing "ready" with model info
- A prompt waiting for input (›)

### 5. Run a Safe Test Command

Try a harmless command:
```
› show current date and time
```

The application should:
1. Display the interpreted shell command in a clean box
2. Ask for confirmation
3. Execute and show the result with minimal, modern formatting

## 🧪 Running Tests

If you want to run the test suite:

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_cli.py

# Run property-based tests
pytest tests/ -k "property"
```

## 📁 Project Structure

```
haunted-terminal-cli/
├── haunted.py              # Main entry point
├── setup.py               # Professional packaging configuration
├── src/
│   ├── cli.py             # CLI interface and main loop
│   ├── theme.py           # Spooky theme and styling
│   ├── ollama_client.py   # Ollama LLM integration
│   ├── executor.py        # Command execution
│   ├── safety.py          # Destructive command detection
│   └── history.py         # SQLite command history
├── tests/                 # Test suite
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## 🎯 Why Use `pip install -e .`?

The professional installation method (`pip install -e .`) offers several advantages:

1. **System-wide Command**: Run `haunted` from any directory
2. **Automatic Dependencies**: All requirements installed automatically
3. **Development Mode**: Edit code and see changes immediately (no reinstall needed)
4. **Standard Practice**: Same approach used by pip, pytest, black, and other professional tools
5. **Easy Uninstall**: Simply run `pip uninstall haunted-terminal-cli`
6. **Virtual Environment Friendly**: Works perfectly with venv, conda, etc.

This is the recommended approach for both development and daily use!

## 🔐 Privacy & Security

- **Offline Operation**: All processing happens locally on your machine
- **No External Calls**: The application only communicates with localhost Ollama
- **Command History**: Stored locally in SQLite database
- **Safety Checks**: Destructive operations require explicit confirmation
- **Open Source**: Review the code to verify privacy claims

## 🎨 Customization

The theme and styling can be customized by editing `src/theme.py`:

- Color palette (teal accent, soft purple secondary, muted gray-green for status)
- Prompt symbols and prefixes
- Message templates
- Loading animations and spinners
- Quiet mode for minimal output

## 📝 License

[Add your license information here]

## 🤝 Contributing

[Add contribution guidelines here]

## 🐛 Known Issues

- First command may be slow as Ollama loads the model into memory
- Very complex commands might not interpret correctly
- Some shell-specific features (pipes, redirects) may need careful phrasing

## 💀 Credits

Built with:
- [Ollama](https://ollama.com/) - Local LLM runtime
- [Typer](https://typer.tiangolo.com/) - CLI framework
- [Rich](https://rich.readthedocs.io/) - Terminal formatting
- [Hypothesis](https://hypothesis.readthedocs.io/) - Property-based testing

---

**👻 Clean, minimal, and modern - your terminal, reimagined.**
