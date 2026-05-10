"""Command executor with environment awareness"""

import subprocess
import os
from ...utils.helpers import SHELL_BUILTINS, PACKAGE_MANAGERS, detect_environment
from ...utils.colors import green, red, yellow, cyan
from .installer import SmartInstaller

class CommandExecutor:
    """Execute system commands with intelligence"""
    
    def __init__(self):
        self.environment = detect_environment()
        self.installer = SmartInstaller()
        self.package_cache = {}
    
    def is_command_available(self, cmd_name: str) -> bool:
        """Check if a command is available"""
        if cmd_name in self.package_cache:
            return self.package_cache[cmd_name]
        
        if cmd_name in SHELL_BUILTINS or cmd_name in PACKAGE_MANAGERS:
            self.package_cache[cmd_name] = True
            return True
        
        result = subprocess.run(f'which {cmd_name}', shell=True, capture_output=True, text=True)
        if result.returncode == 0 and result.stdout.strip():
            self.package_cache[cmd_name] = True
            return True
        
        self.package_cache[cmd_name] = False
        return False
    
    def execute(self, command: str) -> tuple:
        """Execute a command and return output"""
        print(cyan(f"[Executing: {command}]"))
        
        # Extract command name
        cmd_parts = command.split()
        cmd_name = cmd_parts[0]
        if cmd_name == 'sudo' and len(cmd_parts) > 1:
            cmd_name = cmd_parts[1]
        cmd_name = os.path.basename(cmd_name)
        
        # Check if command exists
        if cmd_name not in SHELL_BUILTINS and cmd_name not in PACKAGE_MANAGERS:
            if not self.is_command_available(cmd_name):
                print(yellow(f"[Command '{cmd_name}' not found]"))
                if not self.installer.install(cmd_name):
                    return None, f"Package '{cmd_name}' not available"
        
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=180, executable='/bin/bash')
            if result.returncode == 0:
                print(green("[Command executed successfully]"))
                return result.stdout, result.stderr
            else:
                print(red(f"[Command failed with exit code {result.returncode}]"))
                if result.stderr:
                    print(yellow(f"[Stderr: {result.stderr[:300]}]"))
                return result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            print(red("[Command timeout after 180 seconds]"))
            return None, "Timeout"
        except Exception as e:
            print(red(f"[Failed: {e}]"))
            return None, str(e)