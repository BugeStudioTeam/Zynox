"""Command executor with environment awareness"""

import subprocess
import os
from ...constants import SHELL_BUILTINS, PACKAGE_MANAGERS
from ...utils.helpers import detect_environment
from ...utils.colors import green, red, yellow, cyan
from .installer import SmartInstaller

class CommandExecutor:
    """Execute system commands with intelligence"""
    
    def __init__(self):
        self.environment = detect_environment()
        self.installer = SmartInstaller()
    
    def execute(self, command: str, retry_count: int = 0) -> tuple:
        """Execute a command and return output"""
        print(cyan(f"[Executing: {command}]"))
        
        # Extract command name
        cmd_parts = command.split()
        if not cmd_parts:
            return None, "Empty command"
        
        cmd_name = cmd_parts[0]
        if cmd_name == 'sudo' and len(cmd_parts) > 1:
            cmd_name = cmd_parts[1]
        cmd_name = os.path.basename(cmd_name)
        
        # Check if command exists (skip for shell built-ins and package managers)
        if cmd_name not in SHELL_BUILTINS and cmd_name not in PACKAGE_MANAGERS:
            if not self.installer.is_installed(cmd_name):
                print(yellow(f"[Command '{cmd_name}' not found]"))
                if not self.installer.install(cmd_name):
                    return None, f"Package '{cmd_name}' not available"
        
        try:
            result = subprocess.run(
                command, 
                shell=True, 
                capture_output=True, 
                text=True, 
                timeout=180,
                executable='/bin/bash'
            )
            
            if result.returncode == 0:
                print(green("[Command executed successfully]"))
                if result.stdout and result.stdout.strip():
                    print(result.stdout)
                return result.stdout, result.stderr
            else:
                print(red(f"[Command failed with exit code {result.returncode}]"))
                if result.stderr:
                    print(yellow(f"[Stderr: {result.stderr[:500]}]"))
                return result.stdout, result.stderr
                
        except subprocess.TimeoutExpired:
            print(red("[Command timeout after 180 seconds]"))
            return None, "Timeout"
        except Exception as e:
            print(red(f"[Failed to execute: {e}]"))
            return None, str(e)