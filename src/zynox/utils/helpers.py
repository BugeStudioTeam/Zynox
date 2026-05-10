"""Helper utilities"""

import os
import subprocess
import re

def detect_environment():
    """Detect if running in Termux or Linux"""
    if os.path.exists("/data/data/com.termux/files/usr"):
        return "termux"
    elif os.path.exists("/system/bin/app_process"):
        return "android"
    else:
        return "linux"

def get_package_manager():
    """Get the appropriate package manager"""
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

# Shell built-in commands
SHELL_BUILTINS = {
    'cd', 'cp', 'mv', 'rm', 'mkdir', 'rmdir', 'touch', 'ls', 'cat', 'echo',
    'pwd', 'which', 'alias', 'unalias', 'export', 'unset', 'set', 'env',
    'source', '.', 'exec', 'exit', 'kill', 'type', 'times', 'ulimit',
    'umask', 'wait', 'jobs', 'fg', 'bg', 'shift', 'getopts', 'readonly',
    'printf', 'test', '[', ']', 'true', 'false', 'head', 'tail', 'grep',
    'sed', 'awk', 'find', 'xargs', 'sort', 'uniq', 'wc', 'tr', 'cut'
}

PACKAGE_MANAGERS = {'pkg', 'apt', 'apt-get', 'yum', 'dnf', 'pacman', 'brew', 'sudo'}