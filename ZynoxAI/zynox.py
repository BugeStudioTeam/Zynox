#!/usr/bin/env python3
"""
ZynoxAI - AI-powered file/folder creation tool with memory
Supports: OpenAI, Gemini, Grok, DeepSeek
Telegram Bot Support - Fixed for Termux
"""

import os
import sys
import json
import argparse
import requests
import subprocess
import time
import threading
import asyncio
from pathlib import Path
from colorama import init, Fore, Style
import re
from datetime import datetime
from queue import Queue

# Try to import telegram modules
try:
    from telegram import Update
    from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
    TELEGRAM_AVAILABLE = True
except ImportError:
    TELEGRAM_AVAILABLE = False
    print(f"{Fore.YELLOW}[Telegram module not installed. Run: pip install python-telegram-bot]")

# Initialize colorama for cross-platform colored output
init(autoreset=True)

# Configuration
CONFIG_DIR = os.path.expanduser("~/.zynoxai")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")
MEMORY_DIR = os.path.join(CONFIG_DIR, "memories")
CURRENT_SESSION_FILE = os.path.join(CONFIG_DIR, "current_session.json")
TELEGRAM_CONFIG_FILE = os.path.join(CONFIG_DIR, "telegram_config.json")

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

# Cache for checked packages to avoid repeated checks
PACKAGE_CHECK_CACHE = {}

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

# Global flag for bot running
bot_running = False

def print_logo():
    logo = f"""
{Fore.CYAN}╔═══════════════════════════════════════════════════════════════╗
{Fore.CYAN}║{Fore.YELLOW}   ███████╗██╗   ██╗███╗   ██╗ ██████╗ ██╗  ██╗{Fore.CYAN}                ║
{Fore.CYAN}║{Fore.YELLOW}   ╚══███╔╝╚██╗ ██╔╝████╗  ██║██╔═══██╗╚██╗██╔╝{Fore.CYAN}                ║
{Fore.CYAN}║{Fore.YELLOW}     ███╔╝  ╚████╔╝ ██╔██╗ ██║██║   ██║ ╚███╔╝ {Fore.CYAN}                ║
{Fore.CYAN}║{Fore.YELLOW}    ███╔╝    ╚██╔╝  ██║╚██╗██║██║   ██║ ██╔██╗ {Fore.CYAN}                ║
{Fore.CYAN}║{Fore.YELLOW}   ███████╗   ██║   ██║ ╚████║╚██████╔╝██╔╝ ██╗{Fore.CYAN}                ║
{Fore.CYAN}║{Fore.YELLOW}   ╚══════╝   ╚═╝   ╚═╝  ╚═══╝ ╚═════╝ ╚═╝  ╚═╝{Fore.CYAN}                ║
{Fore.CYAN}╠═══════════════════════════════════════════════════════════════╣
{Fore.CYAN}║{Fore.GREEN}         AI-Powered File & Folder Creation Tool{Fore.CYAN}                ║
{Fore.CYAN}║{Fore.MAGENTA}      ChatGPT • Gemini • Grok • DeepSeek • Telegram{Fore.CYAN}            ║
{Fore.CYAN}╚═══════════════════════════════════════════════════════════════╝{Style.RESET_ALL}
"""
    print(logo)

def detect_environment():
    """Detect if running in Termux or Linux"""
    if os.path.exists("/data/data/com.termux/files/usr"):
        return "termux"
    elif os.path.exists("/system/bin/app_process"):
        return "android"
    else:
        return "linux"

def get_package_manager():
    """Get the appropriate package manager based on environment"""
    env = detect_environment()
    
    if env == "termux" or env == "android":
        return "pkg"
    else:
        if subprocess.run(['which', 'apt'], capture_output=True).returncode == 0:
            return "apt"
        elif subprocess.run(['which', 'yum'], capture_output=True).returncode == 0:
            return "yum"
        elif subprocess.run(['which', 'dnf'], capture_output=True).returncode == 0:
            return "dnf"
        elif subprocess.run(['which', 'pacman'], capture_output=True).returncode == 0:
            return "pacman"
        elif subprocess.run(['which', 'brew'], capture_output=True).returncode == 0:
            return "brew"
        else:
            return "unknown"

def is_command_available(cmd_name: str) -> bool:
    """Check if a command is available (with caching)"""
    if cmd_name in PACKAGE_CHECK_CACHE:
        return PACKAGE_CHECK_CACHE[cmd_name]
    
    if cmd_name in SHELL_BUILTINS:
        PACKAGE_CHECK_CACHE[cmd_name] = True
        return True
    
    if cmd_name in PACKAGE_MANAGERS:
        PACKAGE_CHECK_CACHE[cmd_name] = True
        return True
    
    result = subprocess.run(f'which {cmd_name}', shell=True, capture_output=True, text=True)
    if result.returncode == 0 and result.stdout.strip():
        PACKAGE_CHECK_CACHE[cmd_name] = True
        return True
    
    result = subprocess.run(f'{cmd_name} --version', shell=True, capture_output=True, text=True)
    if result.returncode == 0:
        PACKAGE_CHECK_CACHE[cmd_name] = True
        return True
    
    PACKAGE_CHECK_CACHE[cmd_name] = False
    return False

class MemoryManager:
    def __init__(self):
        os.makedirs(MEMORY_DIR, exist_ok=True)
        self.current_session = self.load_current_session()
    
    def load_current_session(self) -> dict:
        if os.path.exists(CURRENT_SESSION_FILE):
            try:
                with open(CURRENT_SESSION_FILE, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {
            "session_id": f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "messages": [],
            "created_at": datetime.now().isoformat()
        }
    
    def save_current_session(self):
        with open(CURRENT_SESSION_FILE, 'w') as f:
            json.dump(self.current_session, f, indent=2)
    
    def add_message(self, role: str, content: str):
        self.current_session["messages"].append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        self.save_current_session()
    
    def get_conversation_context(self, limit: int = 5) -> str:
        messages = self.current_session["messages"][-limit:]
        if not messages:
            return ""
        context = "\n"
        for msg in messages:
            role = "User" if msg["role"] == "user" else "Assistant"
            context += f"{role}: {msg['content'][:200]}\n"
        return context
    
    def new_session(self):
        session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        if self.current_session["messages"]:
            history_file = os.path.join(MEMORY_DIR, f"{self.current_session['session_id']}.json")
            with open(history_file, 'w') as f:
                json.dump(self.current_session, f, indent=2)
        self.current_session = {
            "session_id": session_id,
            "messages": [],
            "created_at": datetime.now().isoformat()
        }
        self.save_current_session()
        print(f"{Fore.GREEN}[New session created: {session_id}]")
    
    def list_sessions(self) -> list:
        sessions = []
        for file in os.listdir(MEMORY_DIR):
            if file.endswith('.json'):
                with open(os.path.join(MEMORY_DIR, file), 'r') as f:
                    data = json.load(f)
                    sessions.append({
                        "id": data.get("session_id", file.replace('.json', '')),
                        "created": data.get("created_at", "Unknown"),
                        "message_count": len(data.get("messages", []))
                    })
        return sessions
    
    def load_session(self, session_id: str):
        session_file = os.path.join(MEMORY_DIR, f"{session_id}.json")
        if os.path.exists(session_file):
            with open(session_file, 'r') as f:
                self.current_session = json.load(f)
            self.save_current_session()
            print(f"{Fore.GREEN}[Loaded session: {session_id}]")
            return True
        print(f"{Fore.RED}[Session not found: {session_id}]")
        return False
    
    def delete_session(self, session_id: str):
        session_file = os.path.join(MEMORY_DIR, f"{session_id}.json")
        if os.path.exists(session_file):
            os.remove(session_file)
            print(f"{Fore.GREEN}[Deleted session: {session_id}]")
            return True
        print(f"{Fore.RED}[Session not found: {session_id}]")
        return False
    
    def delete_all_sessions(self):
        count = 0
        for file in os.listdir(MEMORY_DIR):
            if file.endswith('.json'):
                os.remove(os.path.join(MEMORY_DIR, file))
                count += 1
        print(f"{Fore.GREEN}[Deleted {count} sessions]")
        self.clear_memory()
    
    def clear_memory(self):
        self.current_session = {
            "session_id": f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "messages": [],
            "created_at": datetime.now().isoformat()
        }
        self.save_current_session()
        print(f"{Fore.GREEN}[Memory cleared, new session started]")

class ZynoxAI:
    def __init__(self):
        self.config = self.load_config()
        self.current_provider = self.config.get("default_provider", "openai")
        self.memory = MemoryManager()
        self.last_command_result = None
        self.task_complete = False
        self.environment = detect_environment()
        self.package_manager = get_package_manager()
        print(f"{Fore.CYAN}[Environment: {self.environment.upper()}]")
        print(f"{Fore.CYAN}[Package Manager: {self.package_manager}]")

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    return json.load(f)
            except:
                return {
                    "api_keys": {},
                    "default_provider": "openai",
                    "default_model": None
                }
        return {
            "api_keys": {},
            "default_provider": "openai",
            "default_model": None
        }

    def save_config(self):
        os.makedirs(CONFIG_DIR, exist_ok=True)
        with open(CONFIG_FILE, 'w') as f:
            json.dump(self.config, f, indent=2)
        print(f"{Fore.GREEN}[Configuration saved]")

    def set_api_key(self, provider: str, api_key: str):
        provider = provider.lower()
        if provider not in API_ENDPOINTS:
            print(f"{Fore.RED}[Unsupported provider: {', '.join(API_ENDPOINTS.keys())}]")
            return False
        self.config["api_keys"][provider] = api_key
        self.save_config()
        print(f"{Fore.GREEN}[API key for {provider} configured]")
        return True

    def set_default_provider(self, provider: str):
        provider = provider.lower()
        if provider not in API_ENDPOINTS:
            print(f"{Fore.RED}[Unsupported provider: {', '.join(API_ENDPOINTS.keys())}]")
            return False
        self.config["default_provider"] = provider
        self.save_config()
        print(f"{Fore.GREEN}[Default provider set to {provider}]")
        self.current_provider = provider
        return True

    def get_install_command(self, package: str) -> str:
        """Get the appropriate install command based on environment"""
        if self.package_manager == "pkg":
            return f"pkg install -y {package}"
        elif self.package_manager == "apt":
            return f"sudo apt install -y {package}"
        elif self.package_manager == "yum":
            return f"sudo yum install -y {package}"
        elif self.package_manager == "dnf":
            return f"sudo dnf install -y {package}"
        elif self.package_manager == "pacman":
            return f"sudo pacman -S --noconfirm {package}"
        elif self.package_manager == "brew":
            return f"brew install {package}"
        else:
            return None

    def search_package_online(self, cmd_name: str) -> list:
        """Search for package online using different methods"""
        print(f"{Fore.CYAN}[Searching online for {cmd_name}...]")
        methods = []
        
        if self.environment == "termux":
            try:
                result = subprocess.run(f"pkg search {cmd_name}", shell=True, capture_output=True, text=True)
                if result.stdout:
                    lines = result.stdout.split('\n')
                    for line in lines:
                        if cmd_name in line.lower():
                            pkg_name = line.split()[0] if line.split() else None
                            if pkg_name:
                                methods.append(("pkg", pkg_name))
            except:
                pass
        
        try:
            import urllib.request
            url = f"https://api.github.com/search/repositories?q={cmd_name}+android+termux&per_page=3"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode())
                for repo in data.get('items', [])[:2]:
                    repo_url = repo.get('html_url', '')
                    install_cmd = f"git clone {repo_url}"
                    methods.append(("git", install_cmd))
        except:
            pass
        
        methods.append(("manual", f"Please search: 'how to install {cmd_name} in {self.environment}'"))
        
        return methods

    def smart_install(self, cmd_name: str) -> bool:
        """Smart installation - tries multiple methods"""
        print(f"{Fore.CYAN}[Smart installing {cmd_name}...]")
        
        standard_packages = {
            'apktool': 'apktool',
            'jadx': 'jadx', 
            'dex2jar': 'dex2jar',
            'jd-gui': 'jd-gui',
            'nmap': 'nmap',
            'hydra': 'hydra',
            'sqlmap': 'sqlmap',
            'metasploit': 'metasploit'
        }
        
        if cmd_name in standard_packages:
            pkg = standard_packages[cmd_name]
            install_cmd = self.get_install_command(pkg)
            if install_cmd:
                confirm = input(f"{Fore.CYAN}Try installing '{pkg}'? (y/N): ")
                if confirm.lower() == 'y':
                    result = subprocess.run(install_cmd, shell=True, capture_output=True)
                    if result.returncode == 0:
                        print(f"{Fore.GREEN}[Installed {pkg} successfully]")
                        PACKAGE_CHECK_CACHE[cmd_name] = True
                        return True
        
        if cmd_name == 'apktool':
            return self.install_apktool()
        elif cmd_name == 'jadx':
            return self.install_jadx()
        elif cmd_name == 'dex2jar':
            return self.install_dex2jar()
        
        methods = self.search_package_online(cmd_name)
        
        if methods:
            print(f"{Fore.CYAN}[Found {len(methods)} installation methods:]")
            for i, (method_type, method_cmd) in enumerate(methods, 1):
                print(f"  {i}. [{method_type}] {method_cmd[:80]}")
            
            choice = input(f"{Fore.CYAN}Choose method (1-{len(methods)}) or 'n' to skip: ")
            if choice.isdigit() and 1 <= int(choice) <= len(methods):
                method_type, method_cmd = methods[int(choice) - 1]
                
                if method_type == "git":
                    confirm = input(f"{Fore.CYAN}Clone and build from source? (y/N): ")
                    if confirm.lower() == 'y':
                        result = subprocess.run(method_cmd, shell=True, capture_output=True)
                        if result.returncode == 0:
                            print(f"{Fore.GREEN}[Cloned successfully]")
                            print(f"{Fore.YELLOW}[You may need to build manually: cd {cmd_name} && ./gradlew build]")
                            return True
                elif method_type == "pkg":
                    confirm = input(f"{Fore.CYAN}Install via pkg? (y/N): ")
                    if confirm.lower() == 'y':
                        result = subprocess.run(method_cmd, shell=True, capture_output=True)
                        if result.returncode == 0:
                            print(f"{Fore.GREEN}[Installed successfully]")
                            PACKAGE_CHECK_CACHE[cmd_name] = True
                            return True
        
        print(f"{Fore.RED}[Could not auto-install {cmd_name}]")
        print(f"{Fore.YELLOW}[Please manually install: pkg search {cmd_name} or search online]")
        return False

    def install_apktool(self) -> bool:
        """Install apktool from multiple sources"""
        print(f"{Fore.CYAN}[Installing apktool...]")
        
        urls = [
            "https://raw.githubusercontent.com/iBotPeaches/Apktool/master/scripts/linux/apktool.jar",
            "https://github.com/iBotPeaches/Apktool/releases/latest/download/apktool.jar",
        ]
        
        os.makedirs(os.path.expandvars("$PREFIX/share/apktool"), exist_ok=True)
        jar_path = os.path.expandvars("$PREFIX/share/apktool/apktool.jar")
        
        for url in urls:
            print(f"{Fore.CYAN}[Trying: {url}]")
            download_cmd = f"wget -O {jar_path} {url} --timeout=10"
            result = subprocess.run(download_cmd, shell=True, capture_output=True)
            if result.returncode == 0 and os.path.exists(jar_path) and os.path.getsize(jar_path) > 1000:
                print(f"{Fore.GREEN}[Downloaded apktool.jar]")
                break
        else:
            print(f"{Fore.RED}[Failed to download apktool.jar]")
            return False
        
        script_path = os.path.expandvars("$PREFIX/bin/apktool")
        script_content = f'''#!/bin/bash
java -jar "{jar_path}" "$@"
'''
        with open(script_path, 'w') as f:
            f.write(script_content)
        os.chmod(script_path, 0o755)
        
        print(f"{Fore.GREEN}[apktool installed successfully]")
        PACKAGE_CHECK_CACHE['apktool'] = True
        return True

    def install_jadx(self) -> bool:
        """Install jadx"""
        print(f"{Fore.CYAN}[Installing jadx...]")
        
        if self.package_manager == "pkg":
            result = subprocess.run("pkg install -y jadx", shell=True, capture_output=True)
            if result.returncode == 0:
                print(f"{Fore.GREEN}[jadx installed]")
                PACKAGE_CHECK_CACHE['jadx'] = True
                return True
        
        print(f"{Fore.RED}[Failed to install jadx]")
        return False

    def install_dex2jar(self) -> bool:
        """Install dex2jar"""
        print(f"{Fore.CYAN}[Installing dex2jar...]")
        
        if self.package_manager == "pkg":
            result = subprocess.run("pkg install -y dex2jar", shell=True, capture_output=True)
            if result.returncode == 0:
                print(f"{Fore.GREEN}[dex2jar installed]")
                PACKAGE_CHECK_CACHE['dex2jar'] = True
                return True
        
        print(f"{Fore.RED}[Failed to install dex2jar]")
        return False

    def check_and_install_package(self, cmd_name: str) -> bool:
        """Check if package is installed, if not ask to install"""
        
        if is_command_available(cmd_name):
            return True
        
        print(f"{Fore.YELLOW}[Package '{cmd_name}' not found]")
        confirm = input(f"{Fore.CYAN}Try to smart install '{cmd_name}'? (y/N): ")
        
        if confirm.lower() == 'y':
            return self.smart_install(cmd_name)
        
        return False

    def execute_command(self, command: str, retry_count: int = 0) -> tuple:
        """Execute a Linux/Unix command with auto-fix for common issues"""
        print(f"{Fore.CYAN}[Executing: {command}]")
        
        cmd_parts = command.split()
        cmd_name = cmd_parts[0]
        if cmd_name == 'sudo' and len(cmd_parts) > 1:
            cmd_name = cmd_parts[1]
        cmd_name = os.path.basename(cmd_name)
        
        if cmd_name not in SHELL_BUILTINS and cmd_name not in PACKAGE_MANAGERS:
            if not is_command_available(cmd_name):
                if not self.check_and_install_package(cmd_name):
                    return None, f"Package '{cmd_name}' not available"
        
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=180, executable='/bin/bash')
            
            if result.returncode == 0:
                print(f"{Fore.GREEN}[Command executed successfully]")
                return result.stdout, result.stderr
            
            stderr = result.stderr.lower() if result.stderr else ""
            
            if "can't find apktool.jar" in stderr or "apktool.jar" in stderr:
                print(f"{Fore.YELLOW}[apktool issue detected, reinstalling...]")
                if self.install_apktool() and retry_count < 2:
                    return self.execute_command(command, retry_count + 1)
            
            elif "java: command not found" in stderr:
                print(f"{Fore.YELLOW}[Java not found, installing...]")
                confirm = input(f"{Fore.CYAN}Install openjdk-17? (y/N): ")
                if confirm.lower() == 'y':
                    install_cmd = self.get_install_command('openjdk-17')
                    if install_cmd:
                        subprocess.run(install_cmd, shell=True)
                        if retry_count < 2:
                            return self.execute_command(command, retry_count + 1)
            
            print(f"{Fore.RED}[Command failed with exit code {result.returncode}]")
            if result.stderr:
                print(f"{Fore.YELLOW}[Stderr: {result.stderr[:300]}]")
            return result.stdout, result.stderr
            
        except subprocess.TimeoutExpired:
            print(f"{Fore.RED}[Command timeout after 180 seconds]")
            return None, "Timeout"
        except Exception as e:
            print(f"{Fore.RED}[Failed: {e}]")
            return None, str(e)

    def find_file(self, filename: str, search_path: str = ".") -> str:
        print(f"{Fore.CYAN}[Searching for: {filename}]")
        cmd = f'find {search_path} -name "{filename}" -type f 2>/dev/null | head -1'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.stdout.strip():
            found_path = result.stdout.strip()
            print(f"{Fore.GREEN}[Found: {found_path}]")
            return found_path
        else:
            print(f"{Fore.YELLOW}[Not found: {filename}]")
            return None

    def find_folder(self, foldername: str, search_path: str = ".") -> str:
        print(f"{Fore.CYAN}[Searching for folder: {foldername}]")
        cmd = f'find {search_path} -type d -name "{foldername}" 2>/dev/null | head -1'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.stdout.strip():
            found_path = result.stdout.strip()
            print(f"{Fore.GREEN}[Found folder: {found_path}]")
            return found_path
        else:
            print(f"{Fore.YELLOW}[Folder not found: {foldername}]")
            return None

    def read_file(self, filepath: str) -> str:
        try:
            if os.path.exists(filepath):
                full_path = filepath
            else:
                searched = self.find_file(os.path.basename(filepath))
                if searched:
                    full_path = searched
                else:
                    return None
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            print(f"{Fore.GREEN}[Read: {full_path} ({len(content)} bytes)]")
            return content
        except Exception as e:
            print(f"{Fore.RED}[Read failed: {e}]")
            return None

    def list_files(self, path: str = ".") -> str:
        try:
            items = os.listdir(path)
            files = [f for f in items if os.path.isfile(os.path.join(path, f))]
            dirs = [d for d in items if os.path.isdir(os.path.join(path, d))]
            result = "Directories:\n" + "\n".join(f"  [DIR] {d}" for d in dirs[:10])
            result += "\n\nFiles:\n" + "\n".join(f"  [FILE] {f}" for f in files[:20])
            if len(files) > 20:
                result += f"\n  ... and {len(files) - 20} more"
            return result
        except Exception as e:
            return f"Error: {e}"

    def create_file(self, path: str, content: str, base_path: str = "."):
        full_path = os.path.join(base_path, path)
        try:
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"{Fore.GREEN}[Created: {path}]")
            return True
        except Exception as e:
            print(f"{Fore.RED}[Failed: {path} - {e}]")
            return False

    def create_folder(self, path: str, base_path: str = "."):
        full_path = os.path.join(base_path, path)
        try:
            os.makedirs(full_path, exist_ok=True)
            print(f"{Fore.GREEN}[Created folder: {path}]")
            return True
        except Exception as e:
            print(f"{Fore.RED}[Failed: {path} - {e}]")
            return False

    def create_prompt(self, user_input: str, context: str = "", file_list: str = "") -> str:
        conversation = self.memory.get_conversation_context(limit=3)
        env_info = f"\n[Environment: {self.environment}, Package Manager: {self.package_manager}]\n"
        
        return f"""You are ZynoxAI. Execute the request and then output COMPLETE.

{env_info}{conversation}
Current directory:
{file_list[:500]}

{context}
User: {user_input}

Output ONE JSON with actions. End with COMPLETE.

Action types:
- SEARCH: {{"type": "search_file", "filename": "name"}}
- READ: {{"type": "read", "path": "path"}}
- LIST: {{"type": "list", "path": "."}}
- FILE: {{"type": "file", "path": "name", "content": "content"}}
- FOLDER: {{"type": "folder", "path": "name"}}
- COMMAND: {{"type": "command", "command": "cmd"}}
- COMPLETE: {{"type": "complete", "message": "done"}}

JSON:"""

    def call_api(self, provider: str, prompt: str, model: str = None, retry: int = 0) -> str:
        if provider not in self.config["api_keys"] or not self.config["api_keys"][provider]:
            print(f"{Fore.RED}[No API key for {provider}]")
            return None
        
        api_key = self.config["api_keys"][provider]
        endpoint_config = API_ENDPOINTS[provider]
        
        if not model:
            model = self.config.get("default_model", endpoint_config["models"][0])
        
        headers = {"Content-Type": "application/json"}
        
        if provider == "deepseek":
            max_tokens_value = 16000
        elif provider == "gemini":
            max_tokens_value = 8192
        else:
            max_tokens_value = 8192
        
        if provider == "gemini":
            url = endpoint_config["url"].replace("{model}", model)
            headers["x-goog-api-key"] = api_key
            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"temperature": 0.1, "maxOutputTokens": max_tokens_value}
            }
        else:
            headers["Authorization"] = f"Bearer {api_key}"
            payload = {
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.1,
                "max_tokens": max_tokens_value
            }
        
        try:
            print(f"{Fore.CYAN}[Thinking...]")
            if provider == "gemini":
                response = requests.post(url, headers=headers, json=payload, timeout=120)
            else:
                response = requests.post(endpoint_config["url"], headers=headers, json=payload, timeout=120)
            
            if response.status_code != 200:
                print(f"{Fore.RED}[HTTP {response.status_code}]")
                if retry < 2:
                    time.sleep(3)
                    return self.call_api(provider, prompt, model, retry + 1)
                return None
            
            result = response.json()
            if provider == "gemini":
                text = result["candidates"][0]["content"]["parts"][0]["text"]
            else:
                text = result["choices"][0]["message"]["content"]
            
            text = re.sub(r'```json\s*', '', text)
            text = re.sub(r'```\s*', '', text)
            return text.strip()
            
        except Exception as e:
            print(f"{Fore.RED}[Error: {e}]")
            if retry < 2:
                time.sleep(3)
                return self.call_api(provider, prompt, model, retry + 1)
            return None

    def parse_and_execute(self, ai_response: str, base_path: str = "."):
        try:
            data = json.loads(ai_response)
        except:
            match = re.search(r'\{.*\}', ai_response, re.DOTALL)
            if match:
                try:
                    data = json.loads(match.group())
                except:
                    print(f"{Fore.RED}[Invalid JSON]")
                    return False
            else:
                print(f"{Fore.RED}[Invalid response]")
                return False
        
        if "type" in data:
            actions = [data]
        elif "actions" in data:
            actions = data["actions"]
        else:
            return False
        
        for action in actions:
            t = action.get("type")
            
            if t == "search_file":
                self.find_file(action.get("filename"), base_path)
            elif t == "search_folder":
                self.find_folder(action.get("foldername"), base_path)
            elif t == "read":
                content = self.read_file(action.get("path"))
                if content:
                    print(f"\n{Fore.CYAN}{'='*50}\n{Fore.WHITE}{content[:1000]}\n{Fore.CYAN}{'='*50}\n")
            elif t == "list":
                print(f"\n{Fore.CYAN}{self.list_files(action.get('path', base_path))}\n")
            elif t == "command":
                stdout, stderr = self.execute_command(action.get("command"))
                if stdout:
                    print(f"{Fore.WHITE}{stdout[:1000]}")
                if stderr:
                    print(f"{Fore.YELLOW}{stderr[:200]}")
            elif t == "file":
                self.create_file(action.get("path"), action.get("content", ""), base_path)
            elif t == "folder":
                self.create_folder(action.get("path"), base_path)
            elif t == "complete":
                print(f"{Fore.GREEN}[Done: {action.get('message', 'Complete')}]")
                self.task_complete = True
                return True
        
        return True

    def run(self, user_input: str, provider: str = None, model: str = None, base_path: str = "."):
        if not user_input:
            return False
        
        self.memory.add_message("user", user_input)
        self.task_complete = False
        
        file_list = self.list_files(base_path)
        prompt = self.create_prompt(user_input, "", file_list)
        response = self.call_api(provider or self.current_provider, prompt, model)
        
        if not response:
            print(f"{Fore.RED}[No response]")
            return False
        
        self.memory.add_message("assistant", response[:300])
        success = self.parse_and_execute(response, base_path)
        
        if not self.task_complete:
            print(f"{Fore.YELLOW}[Task may not be complete]")
        
        return success

class TelegramBotHandler:
    """Telegram Bot Handler - Runs in main thread"""
    
    def __init__(self, zynox_instance, token):
        self.zynox = zynox_instance
        self.token = token
        self.application = None
        self.authorized_users = set()
        self.load_config()
    
    def load_config(self):
        """Load telegram configuration"""
        if os.path.exists(TELEGRAM_CONFIG_FILE):
            try:
                with open(TELEGRAM_CONFIG_FILE, 'r') as f:
                    config = json.load(f)
                    self.authorized_users = set(config.get("authorized_users", []))
            except:
                pass
    
    def save_config(self):
        """Save telegram configuration"""
        config = {
            "authorized_users": list(self.authorized_users),
        }
        with open(TELEGRAM_CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
    
    def is_authorized(self, user_id: int) -> bool:
        """Check if user is authorized"""
        return not self.authorized_users or user_id in self.authorized_users
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        welcome_msg = """
🤖 *ZynoxAI Bot*

AI-powered file and folder creation tool.

*Commands:*
/start - Show this
/help - Show help
/status - Show status
/new - New session
/clear - Clear memory
/history - Show history
/list - List files
/pwd - Show current directory
/cd <path> - Change directory

*Usage:*
Just send any request like:
- "create a python file called hello.py"
- "find abc.txt and read it"
- "list all files"
        """
        await update.message.reply_text(welcome_msg, parse_mode='Markdown')
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_msg = """
*ZynoxAI Bot Commands:*

/new - New conversation session
/clear - Clear current memory
/history - Show conversation history
/status - Show bot status
/list - List files in current directory
/pwd - Show current working directory
/cd <path> - Change directory

*Just type your request naturally!*
        """
        await update.message.reply_text(help_msg, parse_mode='Markdown')
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command"""
        user_id = update.effective_user.id
        if not self.is_authorized(user_id):
            await update.message.reply_text("❌ Unauthorized")
            return
        
        status_msg = f"""
*Bot Status:*
🤖 Bot: Running
🔄 Provider: {self.zynox.current_provider}
💾 Session: {self.zynox.memory.current_session['session_id'][:20]}...
📝 Messages: {len(self.zynox.memory.current_session['messages'])}
🌍 Environment: {self.zynox.environment.upper()}

*System:*
📁 Working Dir: {os.getcwd()}
        """
        await update.message.reply_text(status_msg, parse_mode='Markdown')
    
    async def new_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /new command"""
        user_id = update.effective_user.id
        if not self.is_authorized(user_id):
            await update.message.reply_text("❌ Unauthorized")
            return
        
        self.zynox.memory.new_session()
        await update.message.reply_text("✅ New conversation session created!")
    
    async def clear_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /clear command"""
        user_id = update.effective_user.id
        if not self.is_authorized(user_id):
            await update.message.reply_text("❌ Unauthorized")
            return
        
        self.zynox.memory.clear_memory()
        await update.message.reply_text("✅ Memory cleared!")
    
    async def history_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /history command"""
        user_id = update.effective_user.id
        if not self.is_authorized(user_id):
            await update.message.reply_text("❌ Unauthorized")
            return
        
        messages = self.zynox.memory.current_session.get("messages", [])[-10:]
        if not messages:
            await update.message.reply_text("No conversation history")
            return
        
        history_text = "*Recent Conversation:*\n\n"
        for msg in messages:
            role = "👤 User" if msg["role"] == "user" else "🤖 AI"
            content = msg["content"][:100]
            history_text += f"{role}: {content}\n\n"
        
        await update.message.reply_text(history_text[:4000], parse_mode='Markdown')
    
    async def list_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /list command"""
        user_id = update.effective_user.id
        if not self.is_authorized(user_id):
            await update.message.reply_text("❌ Unauthorized")
            return
        
        files = self.zynox.list_files(".")
        await update.message.reply_text(f"📁 *Current Directory:*\n```\n{files[:3000]}\n```", parse_mode='Markdown')
    
    async def pwd_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /pwd command"""
        user_id = update.effective_user.id
        if not self.is_authorized(user_id):
            await update.message.reply_text("❌ Unauthorized")
            return
        
        await update.message.reply_text(f"📂 Current directory: `{os.getcwd()}`", parse_mode='Markdown')
    
    async def cd_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /cd command"""
        user_id = update.effective_user.id
        if not self.is_authorized(user_id):
            await update.message.reply_text("❌ Unauthorized")
            return
        
        if not context.args:
            await update.message.reply_text("Usage: /cd <path>")
            return
        
        path = context.args[0]
        try:
            os.chdir(path)
            await update.message.reply_text(f"✅ Changed to: `{os.getcwd()}`", parse_mode='Markdown')
        except Exception as e:
            await update.message.reply_text(f"❌ Failed: {e}")
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle regular messages"""
        user_id = update.effective_user.id
        if not self.is_authorized(user_id):
            await update.message.reply_text("❌ Unauthorized. Contact admin to get access.")
            return
        
        user_input = update.message.text
        
        # Send typing indicator
        await update.message.chat.send_action(action="typing")
        
        # Process request
        try:
            # Capture output
            import io
            from contextlib import redirect_stdout
            
            output_buffer = io.StringIO()
            
            with redirect_stdout(output_buffer):
                self.zynox.memory.add_message("user", user_input)
                self.zynox.task_complete = False
                
                file_list = self.zynox.list_files(".")
                prompt = self.zynox.create_prompt(user_input, "", file_list)
                response = self.zynox.call_api(self.zynox.current_provider, prompt)
                
                if response:
                    self.zynox.memory.add_message("assistant", response[:300])
                    self.zynox.parse_and_execute(response, ".")
            
            result = output_buffer.getvalue()
            
            if not result or len(result.strip()) == 0:
                result = "✅ Task completed"
            
            # Split long messages
            if len(result) > 4000:
                for i in range(0, len(result), 4000):
                    await update.message.reply_text(result[i:i+4000])
            else:
                await update.message.reply_text(result)
            
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}")
    
    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle errors"""
        print(f"Telegram error: {context.error}")
        if update and update.effective_message:
            await update.effective_message.reply_text("❌ An error occurred. Please try again.")
    
    def run(self):
        """Run the bot (must be called in main thread)"""
        if not TELEGRAM_AVAILABLE:
            print("Telegram module not installed")
            return False
        
        # Create application
        self.application = Application.builder().token(self.token).build()
        
        # Add handlers
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("status", self.status_command))
        self.application.add_handler(CommandHandler("new", self.new_command))
        self.application.add_handler(CommandHandler("clear", self.clear_command))
        self.application.add_handler(CommandHandler("history", self.history_command))
        self.application.add_handler(CommandHandler("list", self.list_command))
        self.application.add_handler(CommandHandler("pwd", self.pwd_command))
        self.application.add_handler(CommandHandler("cd", self.cd_command))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        self.application.add_error_handler(self.error_handler)
        
        # Start bot (this blocks)
        print(f"{Fore.GREEN}[Telegram Bot Started. Press Ctrl+C to stop]")
        self.application.run_polling(allowed_updates=Update.ALL_TYPES)
        
        return True

def main():
    parser = argparse.ArgumentParser(description="ZynoxAI")
    
    parser.add_argument("--new-session", action="store_true")
    parser.add_argument("--list-sessions", action="store_true")
    parser.add_argument("--load-session", metavar="ID")
    parser.add_argument("--delete-session", metavar="ID")
    parser.add_argument("--delete-all-sessions", action="store_true")
    parser.add_argument("--clear-memory", action="store_true")
    
    parser.add_argument("--set-key", metavar="PROVIDER")
    parser.add_argument("--key")
    parser.add_argument("--set-default", metavar="PROVIDER")
    parser.add_argument("--show-config", action="store_true")
    parser.add_argument("--list-models", action="store_true")
    
    parser.add_argument("--telegram-bot", metavar="TOKEN", help="Start Telegram bot with token")
    
    parser.add_argument("input", nargs="?")
    parser.add_argument("-p", "--provider", choices=["openai", "gemini", "grok", "deepseek"])
    parser.add_argument("-m", "--model")
    parser.add_argument("-d", "--dir", default=".")
    
    args = parser.parse_args()
    
    if len(sys.argv) == 1:
        print_logo()
    
    zynox = ZynoxAI()
    
    # Start Telegram bot if requested (runs in main thread)
    if args.telegram_bot:
        bot = TelegramBotHandler(zynox, args.telegram_bot)
        try:
            bot.run()
        except KeyboardInterrupt:
            print(f"{Fore.YELLOW}[Bot stopped]")
        sys.exit(0)
    
    if args.new_session:
        zynox.memory.new_session()
        sys.exit(0)
    if args.list_sessions:
        sessions = zynox.memory.list_sessions()
        if sessions:
            for s in sessions:
                print(f"  {s['id']} - {s['message_count']} msgs - {s['created'][:19]}")
        else:
            print("[No sessions]")
        sys.exit(0)
    if args.load_session:
        zynox.memory.load_session(args.load_session)
        sys.exit(0)
    if args.delete_session:
        zynox.memory.delete_session(args.delete_session)
        sys.exit(0)
    if args.delete_all_sessions:
        confirm = input("Delete all sessions? (y/N): ")
        if confirm.lower() == 'y':
            zynox.memory.delete_all_sessions()
        sys.exit(0)
    if args.clear_memory:
        zynox.memory.clear_memory()
        sys.exit(0)
    
    if args.set_key:
        if not args.key:
            print("[Need --key]")
            sys.exit(1)
        zynox.set_api_key(args.set_key, args.key)
        sys.exit(0)
    if args.set_default:
        zynox.set_default_provider(args.set_default)
        sys.exit(0)
    if args.list_models:
        for p, info in API_ENDPOINTS.items():
            print(f"\n{p.upper()}:")
            for m in info["models"]:
                print(f"  - {m}")
        sys.exit(0)
    if args.show_config:
        print(f"Default: {zynox.config.get('default_provider', 'None')}")
        print(f"Keys: {', '.join(zynox.config.get('api_keys', {}).keys())}")
        print(f"Session: {zynox.memory.current_session['session_id']}")
        print(f"Messages: {len(zynox.memory.current_session['messages'])}")
        print(f"Environment: {detect_environment().upper()}")
        print(f"Package Manager: {get_package_manager()}")
        sys.exit(0)
    
    if not args.input:
        parser.print_help()
        sys.exit(1)
    
    zynox.run(args.input, args.provider, args.model, args.dir)

if __name__ == "__main__":
    main()