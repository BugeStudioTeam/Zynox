"""Constants for ZynoxAI"""

# Shell built-in commands that don't need installation
SHELL_BUILTINS = {
    'cd', 'cp', 'mv', 'rm', 'mkdir', 'rmdir', 'touch', 'ls', 'cat', 'echo',
    'pwd', 'which', 'alias', 'unalias', 'export', 'unset', 'set', 'env',
    'source', '.', 'exec', 'exit', 'kill', 'type', 'times', 'ulimit',
    'umask', 'wait', 'jobs', 'fg', 'bg', 'shift', 'getopts', 'readonly',
    'printf', 'test', '[', ']', 'true', 'false', 'head', 'tail', 'grep',
    'sed', 'awk', 'find', 'xargs', 'sort', 'uniq', 'wc', 'tr', 'cut'
}

# Package managers - never try to install these
PACKAGE_MANAGERS = {'pkg', 'apt', 'apt-get', 'yum', 'dnf', 'pacman', 'brew', 'sudo'}

# API endpoints for AI providers
API_ENDPOINTS = {
    "openai": {
        "url": "https://api.openai.com/v1/chat/completions",
        "models": ["gpt-3.5-turbo", "gpt-4o-mini", "gpt-4o"]
    },
    "gemini": {
        "url": "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
        "models": ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-2.0-flash-exp"]
    },
    "grok": {
        "url": "https://api.x.ai/v1/chat/completions",
        "models": ["grok-beta", "grok-2-1212", "grok-2-vision-1212"]
    },
    "deepseek": {
        "url": "https://api.deepseek.com/v1/chat/completions",
        "models": ["deepseek-chat", "deepseek-coder"]
    }
}

# Package mapping for smart installation
PACKAGE_MAP = {
    'zip': 'zip', 'unzip': 'unzip', 'tar': 'tar', 'git': 'git',
    'curl': 'curl', 'wget': 'wget', 'ffmpeg': 'ffmpeg',
    'node': 'nodejs', 'npm': 'nodejs', 'pip': 'python-pip',
    'python3': 'python', 'java': 'openjdk-17', 'javac': 'openjdk-17',
    'gcc': 'gcc', 'make': 'make', 'vim': 'vim', 'nano': 'nano',
    'htop': 'htop', 'tree': 'tree', 'find': 'findutils',
    'xargs': 'findutils', 'grep': 'grep', 'sed': 'sed',
    'awk': 'gawk', 'apktool': 'apktool', 'jadx': 'jadx',
    'dex2jar': 'dex2jar', 'nmap': 'nmap', 'hydra': 'hydra',
    'sqlmap': 'sqlmap', 'metasploit': 'metasploit'
}