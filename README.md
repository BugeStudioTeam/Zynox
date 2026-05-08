# 🚀 ZynoxAI - AI-Powered File & Folder Creation Tool

<div align="center">

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.7+-green.svg)
![License](https://img.shields.io/badge/license-MIT-orange.svg)
![Platform](https://img.shields.io/badge/platform-Termux%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)

**Create files and folders using natural language with GPT, Grok, and DeepSeek AI**

[Features](#-features) • [Installation](#-installation) • [Quick Start](#-quick-start) • [Usage Guide](#-usage-guide) • [Examples](#-examples)

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

### Use Cases

- **Rapid Prototyping**: Create complete project structures instantly
- **Learning**: Generate code examples and tutorials
- **Automation**: Script file generation without complex templates
- **Mobile Development**: Run on Termux for on-the-go development
- **Documentation**: Quickly create README, config files, and documentation

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

### Technical Features
- ✅ **Zero Dependencies** - Only requires Python and `requests`
- 🚀 **Lightweight** - Single file, ~25KB, runs anywhere
- 🔄 **Retry Logic** - Automatic retry on network failures
- ⏱️ **Configurable Timeout** - Handles slow connections gracefully
- 🔐 **Secure** - API keys stored locally, never transmitted elsewhere
- 📱 **Termux Optimized** - Works perfectly on Android devices

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

Step 2: Clone/Create ZynoxAI

```bash
# Create directory
mkdir -p ~/ZynoxAI
cd ~/ZynoxAI

# Download the script
curl -o zynox.py https://raw.githubusercontent.com/yourusername/ZynoxAI/main/zynox.py
# OR create manually (copy the code from this repo)
nano zynox.py
```

Step 3: Set Up Alias (Optional but Recommended)

```bash
# Add alias to ~/.bashrc
echo "alias zynox='python ~/ZynoxAI/zynox.py'" >> ~/.bashrc
source ~/.bashrc

# Or for Termux with ~/bin directory
mkdir -p ~/bin
ln -s ~/ZynoxAI/zynox.py ~/bin/zynox
chmod +x ~/ZynoxAI/zynox.py
```

Step 4: Verify Installation

```bash
# Should show the ZYNOX logo
zynox

# Should show help menu
zynox --help
```

---

### 🔧 Configuration

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

### 🚀 Quick Start

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

### 📚 Usage Guide

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
-h, --help Show help message --help

Provider-Specific Tips

OpenAI

· Best for general purpose
· Higher cost but excellent quality
· Use gpt-4o for complex projects
· Use gpt-3.5-turbo for simple tasks

Grok (xAI)

· Great for real-time interactions
· Unique personality and style
· 8K token limit (smaller than others)

DeepSeek

· Best for code generation
· Very cost-effective
· 128K context window (largest)
· Use deepseek-coder for programming tasks

---

### 💡 Examples

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

```python
# Python project structure
zynox "create a Python package with setup.py, README.md, requirements.txt, and src folder with __init__.py"

# Command-line tool
zynox "create a Python CLI tool with argparse that takes a filename and prints its contents"

# Data science project
zynox "create a Jupyter notebook with pandas and matplotlib imports with sample data visualization"
```

System Administration

```bash
# Create backup scripts
zynox "create a bash script that backs up my Downloads folder to a backup directory"

# Configuration files
zynox "create a docker-compose.yml file with nginx, mysql, and phpmyadmin services"

# Log files
zynox "create an error.log and access.log file with initial headers"
```

Document Generation

```bash
# Project documentation
zynox "create a comprehensive README.md with installation, usage, and API documentation sections"

# Configuration files
zynox "create a .env file with API_KEY, DATABASE_URL, and DEBUG variables"

# JSON data
zynox "create a config.json with database settings, API endpoints, and logging configurations"
```

Complex Multi-File Projects

```bash
# Full-stack project
zynox "create a full-stack web app with frontend/index.html, frontend/style.css, frontend/app.js, backend/server.py, and requirements.txt"

# Machine learning project
zynox "create a ML project with data/raw, data/processed, notebooks/analysis.ipynb, src/preprocess.py, src/train.py, and requirements.txt"

# Game development
zynox "create a Python game with main.py, player.py, enemy.py, settings.py, and assets/sprites folder"
```

---

### 📖 Commands Reference

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

### 🔍 Troubleshooting

Common Issues and Solutions

1. Permission Denied Error

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

2. API 400 Error (DeepSeek)

Error:

```bash
✗ HTTP 400 Error: model: invalid type: null
```

Solution:

```bash
# Always specify model
zynox -p deepseek -m deepseek-chat "create file"
```

3. Timeout Error

Error:

```bash
✗ Request timeout
```

Solution:

```bash
# Increase timeout in code (edit zynox.py)
# Find 'timeout=60' and increase to 90 or 120
# Or use a different provider
zynox -p openai "create file"
```

4. JSON Parse Error

Error:

```bash
✗ Failed to parse AI response: Unterminated string
```

Solution:

```bash
# Simplify your request
zynox "create a simple text file"  # Instead of complex HTML
# Or increase max_tokens in code
```

5. API Key Not Working

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

Debug Mode

```bash
# Run with full Python error output
python ~/ZynoxAI/zynox.py "test" 2>&1

# Check raw API response (edit zynox.py to print response.text)
```

---

### 🔑 API Keys

Where to Get API Keys

Provider Sign Up URL Cost Free Tier
OpenAI platform.openai.com Pay-as-you-go $5 free credit
Gemini https://aistudio.google.com/app/apikey Pay-as-you-go / Free tier available
Grok (xAI) console.x.ai Pay-as-you-go Limited free
DeepSeek platform.deepseek.com Very cheap ¥10M free tokens

Setting Up API Keys

1. Create an account at the provider's website
2. Navigate to API Keys section
3. Generate a new API key
4. Copy the key (starts with sk- typically)
5. Set it in ZynoxAI: zynox --set-key PROVIDER --key YOUR_KEY

Security Best Practices

· ✅ Store keys only in local config file
· ✅ Never commit config.json to git
· ✅ Use environment variables for CI/CD
· ✅ Rotate keys periodically
· ❌ Don't share your keys publicly
· ❌ Don't hardcode keys in scripts

---

📁 Project Structure

```
~/
├── ZynoxAI/
│   └── zynox.py              # Main script
└── .zynoxai/
    └── config.json           # Configuration file (auto-created)
```

File Descriptions

· zynox.py: Main executable script
· config.json: Stores API keys and preferences
· ~/.bashrc: Alias configuration (optional)

---

### 🤝 Contributing

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
pip install requests colorama black flake8

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
· Support for more AI providers (Claude, Gemini)
· File content editing/updating
· Git integration
