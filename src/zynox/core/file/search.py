"""File search utilities"""

import subprocess
import os
from ...utils.colors import green, yellow, cyan

class FileSearcher:
    """Search for files and folders"""
    
    @staticmethod
    def find_file(filename: str, search_path: str = ".") -> str:
        """Search for a file using find command"""
        print(cyan(f"[Searching for: {filename}]"))
        cmd = f'find {search_path} -name "{filename}" -type f 2>/dev/null | head -1'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.stdout.strip():
            found_path = result.stdout.strip()
            print(green(f"[Found: {found_path}]"))
            return found_path
        print(yellow(f"[Not found: {filename}]"))
        return None
    
    @staticmethod
    def find_folder(foldername: str, search_path: str = ".") -> str:
        """Search for a folder using find command"""
        print(cyan(f"[Searching for folder: {foldername}]"))
        cmd = f'find {search_path} -type d -name "{foldername}" 2>/dev/null | head -1'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.stdout.strip():
            found_path = result.stdout.strip()
            print(green(f"[Found folder: {found_path}]"))
            return found_path
        print(yellow(f"[Folder not found: {foldername}]"))
        return None