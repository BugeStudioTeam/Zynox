```markdown
# 🚀 ZynoxAI - AI-Powered File & Folder Creation Tool

<div align="center">

![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.7+-green.svg)
![License](https://img.shields.io/badge/license-MIT-orange.svg)
![Platform](https://img.shields.io/badge/platform-Termux%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)

**Create files and folders using natural language with GPT, Gemini, Grok, and DeepSeek AI**

[Features](#-features) • [Installation](#-installation) • [Quick Start](#-quick-start) • [Usage Guide](#-usage-guide) • [Examples](#-examples) • [Telegram Bot](#-telegram-bot)

</div>

---

## 📋 Table of Contents

- [What is ZynoxAI?](#-what-is-zynoxai)
- [Features](#-features)
- [Supported AI Providers](#-supported-ai-providers)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Quick Start](#-quick-start)
- [Usage Guide](#-usage-guide)
- [Examples](#-examples)
- [Commands Reference](#-commands-reference)
- [Telegram Bot](#-telegram-bot)
- [Smart Installation](#-smart-installation)
- [Memory & Sessions](#-memory--sessions)
- [Troubleshooting](#-troubleshooting)
- [API Keys](#-api-keys)
- [Project Structure](#-project-structure)
- [Contributing](#-contributing)

---

## 🤖 What is ZynoxAI?

ZynoxAI is a command-line tool that leverages artificial intelligence to create files and folders based on natural language descriptions. Instead of manually typing `mkdir`, `touch`, and writing file contents, you can simply describe what you want in plain English, and ZynoxAI will:

- Parse your request using AI (GPT, Gemini, Grok, or DeepSeek)
- Generate appropriate file/folder structures
- Create them automatically on your filesystem
- Execute system commands intelligently
- Auto-install missing packages

### Use Cases

- **Rapid Prototyping**: Create complete project structures instantly
- **Learning**: Generate code examples and tutorials
- **Automation**: Script file generation without complex templates
- **Mobile Development**: Run on Termux for on-the-go development
- **Documentation**: Quickly create README, config files, and documentation
- **Remote Control**: Use Telegram bot to control from anywhere

---

## ✨ Features

### Core Features
- 🤖 **Multi-AI Support** - Switch between OpenAI GPT, Google Gemini, Grok (xAI), and DeepSeek
- 🌐 **Natural Language** - Describe what you want in plain English
- 📁 **Batch Operations** - Create multiple files/folders in one command
- 🎨 **Nested Structures** - Automatically creates parent directories
- 🎯 **Smart File Detection** - AI understands file types and extensions
- 📝 **Code Generation** - Creates meaningful code content automatically
- 🎨 **Color Output** - Beautiful terminal interface with colored logs
- 💾 **Persistent Config** - Saves API keys and preferences locally
- 🧠 **Memory System** - Remembers previous conversations and context
- 💬 **Telegram Bot** - Control ZynoxAI remotely via Telegram
- 🔧 **Smart Installation** - Auto-detects and installs missing packages

### Technical Features
- ✅ **Zero Dependencies** - Only requires Python and `requests`
- 🚀 **Lightweight** - Single file, ~25KB, runs anywhere
- 🔄 **Retry Logic** - Automatic retry on network failures
- ⏱️ **Configurable Timeout** - Handles slow connections gracefully
- 🔐 **Secure** - API keys stored locally, never transmitted elsewhere
- 📱 **Termux Optimized** - Works perfectly on Android devices
- 🌍 **Cross-Platform** - Works on Termux, Linux, macOS, Windows

---

## 🧠 Supported AI Providers

| Provider | Models | Best For | Token Limit |
|----------|--------|----------|-------------|
| **OpenAI** | `gpt-3.5-turbo`<br>`gpt-4o-mini`<br>`gpt-4o` | General purpose, high quality | 8K-16K |
| **Gemini** | `gemini-1.5-flash`<br>`gemini-1.5-pro`<br>`gemini-2.0-flash-exp` | Real-time, code, high quality | 8K |
| **Grok** | `grok-beta`<br>`grok-2-1212`<br>`grok-2-vision-1212` | Real-time, witty responses | 8K |
| **DeepSeek** | `deepseek-chat`<br>`deepseek-coder` | Code generation, cost-effective | 128K |

---

## 📦 Installation

### Prerequisites
- Python 3.7 or higher
- pip (Python package manager)
- Internet connection (for API calls)

### Step 1: Install Dependencies

```bash
# Update package manager
pkg update && pkg upgrade  # For Termux
# OR
sudo apt update && sudo apt upgrade  # For Linux

# Install Python if not installed
pkg install python  # Termux
# OR
sudo apt install python3  # Linux

# Install required Python packages
pip install requests colorama
```

### Step 2: Clone/Create ZynoxAI

```bash
# Create directory
mkdir -p ~/ZynoxAI
cd ~/ZynoxAI

# Download the script
wget https://raw.githubusercontent.com/BugeStudioTeam/Zynox/refs/heads/main/ZynoxAI/zynox.py
# OR create manually (copy the code from this repo)
nano zynox.py
```

### Step 3: Set Up Alias (Optional but Recommended)

```bash
# Add alias to ~/.bashrc
echo "alias zynox='python ~/ZynoxAI/zynox.py'" >> ~/.bashrc
source ~/.bashrc

# Or for Termux with ~/bin directory
mkdir -p ~/bin
ln -s ~/ZynoxAI/zynox.py ~/bin/zynox
chmod +x ~/ZynoxAI/zynox.py
```

### Step 4: Verify Installation

```bash
# Should show the ZYNOX logo
zynox

# Should show help menu
zynox --help
```

---

## 🔧 Configuration

Setting API Keys

You need to set API keys for the providers you want to use:

```bash
# OpenAI (get from: https://platform.openai.com/api-keys)
zynox --set-key openai --key sk-your-openai-key

# Gemini (get from: https://aistudio.google.com/app/apikey)
zynox --set-key gemini --key YOUR_GEMINI_API_KEY

# Grok/xAI (get from: https://console.x.ai/)
zynox --set-key grok --key xai-your-grok-key

# DeepSeek (get from: https://platform.deepseek.com/api_keys)
zynox --set-key deepseek --key sk-your-deepseek-key
```

Setting Default Provider

```bash
# Set OpenAI as default
zynox --set-default openai

# Set Gemini as default
zynox --set-default gemini

# Set Grok as default
zynox --set-default grok

# Set DeepSeek as default
zynox --set-default deepseek
```

Viewing Configuration

```bash
# Show current settings
zynox --show-config
```

Example Output:

```
Current Configuration:
  Default Provider: deepseek
  Default Model: deepseek-chat
  Configured APIs: openai, deepseek
```

Configuration File Location

```bash
~/.zynoxai/config.json
```

Example config.json:

```json
{
  "api_keys": {
    "openai": "sk-xxx",
    "deepseek": "sk-yyy"
  },
  "default_provider": "deepseek",
  "default_model": "deepseek-chat"
}
```

---

## 🚀 Quick Start

Basic Usage

```bash
# Create a single file
zynox "create a hello.txt file"

# Create a folder
zynox "create a folder called my_project"

# Create a file with content
zynox "create a python file called hello.py with print('Hello World')"

# Create multiple items
zynox "create a web project with index.html, style.css, and script.js"
```

Using Specific Providers

```bash
# Use OpenAI
zynox -p openai "create a config.json file"

# Use Gemini
zynox -p gemini "create a index.html file"

# Use Grok
zynox -p grok "create a bash script called backup.sh"

# Use DeepSeek with specific model
zynox -p deepseek -m deepseek-coder "create a python api server"
```

Working in Different Directories

```bash
# Create in current directory (default)
zynox "create test.txt"

# Create in specific directory
zynox -d ./myapp "create main.py and requirements.txt"

# Create in absolute path (Termux shared storage)
zynox -d /sdcard/Documents "create notes.txt"
```

---

## 📚 Usage Guide

Command Structure

```bash
zynox [OPTIONS] "YOUR NATURAL LANGUAGE REQUEST"
```

Options

Option Description Example
-p, --provider AI provider to use -p openai, -p deepseek
-m, --model Specific model name -m gpt-4o, -m deepseek-chat
-d, --dir Base directory for creation -d ./project
--set-key Set API key for provider --set-key openai --key sk-xxx
--set-default Set default provider --set-default deepseek
--list-models Show available models --list-models
--show-config Show current configuration --show-config
--new-session Start new conversation session --new-session
--list-sessions List all saved sessions --list-sessions
--load-session Load a previous session --load-session ID
--delete-session Delete a session --delete-session ID
--clear-memory Clear current session memory --clear-memory
-h, --help Show help message --help

Provider-Specific Tips

OpenAI

· Best for general purpose
· Higher cost but excellent quality
· Use gpt-4o for complex projects
· Use gpt-3.5-turbo for simple tasks

Gemini

· Free tier available
· Great for code generation
· Fast response times
· Use gemini-1.5-flash for speed

Grok (xAI)

· Great for real-time interactions
· Unique personality and style
· 8K token limit

DeepSeek

· Best for code generation
· Very cost-effective
· 128K context window (largest)
· Use deepseek-coder for programming tasks

---

## 💡 Examples

Web Development Projects

```bash
# Create a complete HTML/CSS/JS project
zynox "create a modern website with index.html, styles.css, script.js, and an assets folder"

# Create a React component
zynox "create a React component called Button.jsx with props for onClick and children"

# Create a REST API
zynox -p deepseek -m deepseek-coder "create a Flask API with endpoints for GET, POST, and DELETE"
```

Programming Projects

```bash
# Python project structure
zynox "create a Python package with setup.py, README.md, requirements.txt, and src folder with __init__.py"

# Command-line tool
zynox "create a Python CLI tool with argparse that takes a filename and prints its contents"

# Data science project
zynox "create a Jupyter notebook with pandas and matplotlib imports"
```

System Administration

```bash
# Create backup scripts
zynox "create a bash script that backs up my Downloads folder"

# Configuration files
zynox "create a docker-compose.yml file with nginx and mysql"

# Execute commands
zynox "list all files in current directory"
zynox "show disk usage"
```

File Operations

```bash
# Search and read files
zynox "find abc.txt and read it"

# Create based on existing files
zynox "find config.yml and create a similar python script"

# Batch operations
zynox "create a zip file with all python files"
```

---

## 📖 Commands Reference

Configuration Commands

```bash
# Set API keys
zynox --set-key openai --key sk-xxx
zynox --set-key gemini --key YOUR_GEMINI_API_KEY
zynox --set-key grok --key xai-xxx
zynox --set-key deepseek --key sk-xxx

# Set defaults
zynox --set-default openai
zynox --set-default gemini
zynox --set-default grok
zynox --set-default deepseek

# View settings
zynox --show-config
zynox --list-models
```

Session Management Commands

```bash
# Start new conversation
zynox --new-session

# List all saved sessions
zynox --list-sessions

# Load a previous session
zynox --load-session session_20241208_143022

# Delete a session
zynox --delete-session session_20241208_143022

# Clear current memory
zynox --clear-memory
```

Creation Commands

```bash
# Single file
zynox "create a file called example.txt"
zynox "create a text file with content 'Hello World'"

# Single folder
zynox "create a folder called my_directory"
zynox "make a directory named src"

# Multiple items
zynox "create a folder named data and inside it create input.txt and output.txt"
zynox "create index.html, about.html, and contact.html files"

# Nested structures
zynox "create src/utils/helpers.py with a helper function"
zynox "create project/css/style.css with basic styling"
```

Advanced Usage

```bash
# Specify provider and model
zynox -p deepseek -m deepseek-coder "create an algorithm for fibonacci"

# Work in specific directory
zynox -d ~/Desktop "create a shortcut.sh file"

# Combination
zynox -p openai -d ./api "create a REST API with Flask"
```

---

## 💬 Telegram Bot

What is the Telegram Bot?

ZynoxAI includes a Telegram bot that allows you to control the tool remotely from your phone or any device with Telegram. You can create files, run commands, and manage your projects from anywhere.

Setting Up the Telegram Bot

1. Create a bot with BotFather
   · Open Telegram and search for @BotFather
   · Send /newbot and follow the instructions
   · Copy the bot token (format: 1234567890:ABCdefGHIJKLMNopqRsTUVwxyz)
2. Install Telegram dependency

```bash
pip install python-telegram-bot
```

### 1. Start the bot

```bash
python zynox.py --telegram-bot YOUR_BOT_TOKEN
```

Telegram Bot Commands

Command Description
/start Show welcome message
/help Show help menu
/status Show bot and system status
/new Start new conversation session
/clear Clear current memory
/history Show conversation history
/list List files in current directory
/pwd Show current working directory
/cd <path> Change directory

Using the Telegram Bot

Simply send any natural language request to your bot:

```
User: "create a python file called test.py with print('Hello')"
Bot: [Executes and returns result]

User: "find abc.txt and read it"
Bot: [Searches and displays content]

User: "list all files"
Bot: [Shows directory listing]
```

Running Bot in Background (Termux)

```bash
# Run in background
nohup python zynox.py --telegram-bot YOUR_BOT_TOKEN > bot.log 2>&1 &

# Check logs
tail -f bot.log

# Stop bot
pkill -f "zynox.py"
```

Security

· First user who interacts with the bot becomes admin
· Admin can authorize other users with /authorize <user_id>
· All commands require authorization (except first user)

---

## 🔧 Smart Installation

Automatic Package Detection

ZynoxAI automatically detects when a command is not available and offers to install it:

```bash
[Executing: zip files.zip *.txt]
[Package 'zip' not found]
Try to smart install 'zip'? (y/N): y
[Installing zip...]
[Installed zip successfully]
[Command executed successfully]
```

Supported Package Managers

Environment Package Manager
Termux pkg
Debian/Ubuntu apt
RHEL/CentOS yum/dnf
Arch Linux pacman
macOS brew

Special Tool Installation

ZynoxAI can automatically install specialized tools:

· apktool - For APK decompilation (auto-downloads from GitHub)
· jadx - For Java/Android decompilation
· dex2jar - For DEX to JAR conversion

Manual Installation Fallback

If automatic installation fails, ZynoxAI provides manual instructions:

```bash
[Could not auto-install apktool]
[Please manually install: pkg search apktool or search online]
```

---

## 🧠 Memory & Sessions

How Memory Works

ZynoxAI remembers your conversation context across multiple commands:

```bash
# First command
zynox "find abc.txt"
[Found: ./ZynoxAI/abc.txt]

# Second command (remembers previous)
zynox "read it"
[Read: ./ZynoxAI/abc.txt (123 bytes)]
```

Session Management

```bash
# Start a fresh session
zynox --new-session

# List all saved sessions
zynox --list-sessions
# Output:
#   session_20241208_143022 - 5 msgs - 2024-12-08T14:30:22
#   session_20241207_091345 - 12 msgs - 2024-12-07T09:13:45

# Load a previous session
zynox --load-session session_20241208_143022

# Delete a session
zynox --delete-session session_20241207_091345

# Clear current memory
zynox --clear-memory
```

Session Storage

Sessions are stored in ~/.zynoxai/memories/ as JSON files. Each session contains:

· Session ID and creation timestamp
· Full conversation history
· Message timestamps

---

## 🔍 Troubleshooting

Common Issues and Solutions

### 1. Permission Denied Error

Error:

```bash
bash: /data/data/com.termux/files/home/bin/zynox: Permission denied
```

Solution:

```bash
# Use alias instead
echo "alias zynox='python ~/ZynoxAI/zynox.py'" >> ~/.bashrc
source ~/.bashrc
```

### 2. API 400 Error (DeepSeek)

Error:

```bash
✗ HTTP 400 Error: model: invalid type: null
```

Solution:

```bash
# Always specify model
zynox -p deepseek -m deepseek-chat "create file"
```

### 3. Timeout Error

Error:

```bash
✗ Request timeout
```

Solution:

```bash
# Use a different provider
zynox -p openai "create file"
# Or simplify your request
zynox "create a simple text file"
```

### 4. JSON Parse Error

Error:

```bash
✗ Failed to parse AI response: Unterminated string
```

Solution:

```bash
# Simplify your request
zynox "create a simple text file"  # Instead of complex HTML
```

### 5. API Key Not Working

Solution:

```bash
# Verify key is set
zynox --show-config

# Re-set the key
zynox --set-key deepseek --key sk-new-key

# Check key validity (curl test)
curl -X POST https://api.deepseek.com/v1/chat/completions \
  -H "Authorization: Bearer YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model": "deepseek-chat", "messages": [{"role": "user", "content": "Hi"}]}'
```

### 6. Telegram Bot Not Starting

Error:

```
RuntimeError: set_wakeup_fd only works in main thread
```

Solution:
Use the fixed version that runs bot in main thread (included in the code).

Debug Mode

```bash
# Run with full Python error output
python ~/ZynoxAI/zynox.py "test" 2>&1

# Check raw API response (edit zynox.py to print response.text)
```

---

## 🔑 API Keys

Where to Get API Keys

Provider Sign Up URL Cost Free Tier
OpenAI platform.openai.com Pay-as-you-go $5 free credit
Gemini aistudio.google.com Pay-as-you-go Free tier available
Grok (xAI) console.x.ai Pay-as-you-go Limited free
DeepSeek platform.deepseek.com Very cheap ¥10M free tokens

Setting Up API Keys

1. Create an account at the provider's website
2. Navigate to API Keys section
3. Generate a new API key
4. Copy the key (starts with sk- typically for OpenAI/DeepSeek)
5. Set it in ZynoxAI: zynox --set-key PROVIDER --key YOUR_KEY

Security Best Practices

· ✅ Store keys only in local config file
· ✅ Never commit config.json to git
· ✅ Use environment variables for CI/CD
· ✅ Rotate keys periodically
· ❌ Don't share your keys publicly
· ❌ Don't hardcode keys in scripts

---

## 📁 Project Structure

```
~/
├── ZynoxAI/
│   └── zynox.py              # Main script
└── .zynoxai/
    ├── config.json           # Configuration file (auto-created)
    ├── memories/             # Session storage directory
    │   ├── session_xxx.json  # Saved conversation sessions
    │   └── ...
    └── telegram_config.json  # Telegram bot configuration
```

File Descriptions

· zynox.py: Main executable script
· config.json: Stores API keys and preferences
· memories/: Directory containing saved conversation sessions
· telegram_config.json: Stores Telegram bot authorized users
· ~/.bashrc: Alias configuration (optional)

---

## 🤝 Contributing

How to Contribute

1. Fork the repository
2. Create a feature branch: git checkout -b feature/amazing-feature
3. Commit changes: git commit -m 'Add amazing feature'
4. Push to branch: git push origin feature/amazing-feature
5. Open a Pull Request

Development Setup

```bash
# Clone your fork
git clone https://github.com/yourusername/ZynoxAI.git
cd ZynoxAI

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dev dependencies
pip install requests colorama python-telegram-bot black flake8

# Run tests (manual testing for now)
python zynox.py "create test.txt"
```

Code Style

· Follow PEP 8 guidelines
· Use descriptive variable names
· Add docstrings for functions
· Test on Python 3.7+

Feature Ideas

· Support for local LLMs (Ollama, LM Studio)
· Batch operations from file
· Template system for common structures
· Undo/redo functionality
· GUI wrapper (Tkinter/PyQt)
· VS Code extension
· Support for more AI providers (Claude)
· File content editing/updating
· Git integration
· Web interface
· Docker support

---

📄 License

MIT License

---

## 🙏 Acknowledgments

· OpenAI for GPT models
· Google for Gemini models
· xAI for Grok models
· DeepSeek for their excellent code generation models
· python-telegram-bot for Telegram integration
· Termux team for making Linux on Android possible
· All contributors who help improve this tool
