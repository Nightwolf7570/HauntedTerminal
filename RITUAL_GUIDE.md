# 🔮 Haunted Terminal - Ritual/Workflow Guide

## What are Rituals?

Rituals are multi-step command workflows that automate sequences of commands. Perfect for deployment, testing, or any repetitive tasks.

## Fixed Issue

**Problem**: The ritual creation prompt was showing "(y/n)" and not accepting input properly.

**Solution**: Fixed the input handling to use clean prompts without confirmation text.

## How to Create a Ritual

### Step 1: Start Creation

```bash
ritual create my-workflow
```

### Step 2: Enter Description (Optional)

```
Description (optional): Deploy my application
```

### Step 3: Add Commands

```
Enter commands one by one. Type 'done' to finish.

step 1 > git add .
  ✓ added
step 2 > git commit -m "Update"
  ✓ added
step 3 > git push origin main
  ✓ added
step 4 > done

✓ SPELL CAST · ritual 'my-workflow' saved with 3 steps
```

## Managing Rituals

### List All Rituals
```bash
ritual list
```

### Show Ritual Details
```bash
ritual show my-workflow
```

### Run a Ritual
```bash
ritual run my-workflow
```

### Delete a Ritual
```bash
ritual delete my-workflow
```

## Example Rituals

### Git Workflow
```bash
ritual create git-sync
Description: Sync with remote
step 1 > git fetch origin
step 2 > git pull origin main
step 3 > git status
step 4 > done
```

### Testing Suite
```bash
ritual create run-tests
Description: Run all tests
step 1 > python3 -m pytest tests/ -v
step 2 > python3 -m pytest tests/test_ollama_client.py
step 3 > echo "Tests complete!"
step 4 > done
```

### Cleanup
```bash
ritual create cleanup
Description: Clean temporary files
step 1 > find . -name "*.pyc" -delete
step 2 > find . -name "__pycache__" -type d -exec rm -rf {} +
step 3 > rm -rf .pytest_cache
step 4 > done
```

### Deployment
```bash
ritual create deploy
Description: Deploy to production
step 1 > git pull origin main
step 2 > npm install
step 3 > npm run build
step 4 > pm2 restart app
step 5 > done
```

## Quick Reference

| Command | Description |
|---------|-------------|
| `ritual` | Show available rituals |
| `ritual list` | List all rituals |
| `ritual create <name>` | Create new ritual |
| `ritual show <name>` | Show ritual details |
| `ritual run <name>` | Execute ritual |
| `ritual delete <name>` | Delete ritual |

## Tips

1. **Keep steps simple**: Each step should be a single command
2. **Use descriptive names**: Makes rituals easier to find
3. **Add descriptions**: Helps remember what each ritual does
4. **Test first**: Run commands manually before adding to ritual
5. **Error handling**: Rituals stop on first failure

## Storage

Rituals are stored in: `~/.haunted/history.db`

They persist across sessions and can be shared by copying the database file.

## Troubleshooting

**Issue**: Ritual not accepting input  
**Solution**: This has been fixed! Just type your commands normally.

**Issue**: Ritual fails on a step  
**Solution**: Rituals stop on first failure. Check the command and fix it, then recreate the ritual.

**Issue**: Can't find ritual  
**Solution**: Use `ritual list` to see all available rituals.

## Now Try It!

```bash
# Start Haunted Terminal
python3 haunted.py

# Create your first ritual
ritual create hello
Description: Say hello
step 1 > echo "Hello from ritual!"
step 2 > date
step 3 > done

# Run it
ritual run hello
```

Enjoy automating your workflows! 🔮✨
