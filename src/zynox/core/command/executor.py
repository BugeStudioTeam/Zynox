"""Command executor with environment awareness"""

import subprocess
import os
from ...constants import SHELL_BUILTINS, PACKAGE_MANAGERS
from ...utils.helpers import detect_environment
from ...utils.colors import green, red, yellow, cyan
from .installer import SmartInstaller
from ...config import Config

class CommandExecutor:
    """Execute system commands with intelligence"""
    
    def __init__(self):
        self.environment = detect_environment()
        self.installer = SmartInstaller()
        self.create_dir = Config.get_create_dir()
    
    def is_command_available(self, cmd_name: str) -> bool:
        """Check if a command is available (with caching)"""
        if cmd_name in self.installer.package_cache:
            return self.installer.package_cache[cmd_name]
        
        if cmd_name in SHELL_BUILTINS or cmd_name in PACKAGE_MANAGERS:
            self.installer.package_cache[cmd_name] = True
            return True
        
        result = subprocess.run(f'which {cmd_name}', shell=True, capture_output=True, text=True)
        if result.returncode == 0 and result.stdout.strip():
            self.installer.package_cache[cmd_name] = True
            return True
        
        result = subprocess.run(f'{cmd_name} --version', shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            self.installer.package_cache[cmd_name] = True
            return True
        
        self.installer.package_cache[cmd_name] = False
        return False
    
    def execute(self, command: str, retry_count: int = 0) -> tuple:
        """Execute a command and return output"""
        print(cyan(f"[Executing: {command}]"))
        
        # Change to create directory for file operations
        original_cwd = os.getcwd()
        os.chdir(self.create_dir)
        
        # Extract command name
        cmd_parts = command.split()
        if not cmd_parts:
            os.chdir(original_cwd)
            return None, "Empty command"
        
        cmd_name = cmd_parts[0]
        if cmd_name == 'sudo' and len(cmd_parts) > 1:
            cmd_name = cmd_parts[1]
        cmd_name = os.path.basename(cmd_name)
        
        # Check if command exists (skip for shell built-ins and package managers)
        if cmd_name not in SHELL_BUILTINS and cmd_name not in PACKAGE_MANAGERS:
            if not self.is_command_available(cmd_name):
                print(yellow(f"[Command '{cmd_name}' not found]"))
                if not self.installer.install(cmd_name):
                    os.chdir(original_cwd)
                    return None, f"Package '{cmd_name}' not available"
        
        try:
            # Use shell=True to handle built-ins like cd, pipes, redirects
            result = subprocess.run(
                command, 
                shell=True, 
                capture_output=True, 
                text=True, 
                timeout=600,
                executable='/bin/bash',
                cwd=self.create_dir
            )
            
            if result.returncode == 0:
                print(green("[Command executed successfully]"))
                if result.stdout and result.stdout.strip():
                    print(result.stdout)
                os.chdir(original_cwd)
                return result.stdout, result.stderr
            else:
                print(red(f"[Command failed with exit code {result.returncode}]"))
                if result.stderr:
                    print(yellow(f"[Stderr: {result.stderr[:500]}]"))
                # Still return stdout/stderr even on failure
                os.chdir(original_cwd)
                return result.stdout, result.stderr
                
        except subprocess.TimeoutExpired:
            print(red("[Command timeout after 600 seconds]"))
            os.chdir(original_cwd)
            return None, "Timeout"
        except subprocess.CalledProcessError as e:
            print(red(f"[Command failed: {e}]"))
            os.chdir(original_cwd)
            return e.stdout, e.stderr
        except Exception as e:
            print(red(f"[Failed to execute: {e}]"))
            os.chdir(original_cwd)
            return None, str(e)