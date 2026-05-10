"""File and folder management"""

import os
import shutil
from ...config import Config
from ...utils.colors import green, red, cyan

class FileManager:
    """Manage file and folder operations"""
    
    @staticmethod
    def get_absolute_path(path: str, base_path: str = ".") -> str:
        """
        Get absolute path for file creation.
        All created files go to output/create/ directory.
        """
        create_dir = Config.get_create_dir()
        
        # If path starts with output/create/, use as-is
        if path.startswith(create_dir):
            return path
        
        # If path is relative, place in output/create/
        if not os.path.isabs(path):
            return os.path.join(create_dir, path)
        
        # For absolute paths, preserve structure under output/create/
        # Remove leading slash to avoid double slashes
        clean_path = path.lstrip('/')
        return os.path.join(create_dir, clean_path)
    
    @staticmethod
    def create_file(path: str, content: str, base_path: str = ".") -> bool:
        """Create a file with content in output/create/ directory"""
        full_path = FileManager.get_absolute_path(path, base_path)
        try:
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            # Show relative path from output/create/
            rel_path = os.path.relpath(full_path, Config.get_create_dir())
            print(green(f"[Created file: {rel_path}]"))
            return True
        except Exception as e:
            print(red(f"[Failed to create file: {path} - {e}]"))
            return False
    
    @staticmethod
    def create_folder(path: str, base_path: str = ".") -> bool:
        """Create a folder in output/create/ directory"""
        full_path = FileManager.get_absolute_path(path, base_path)
        try:
            os.makedirs(full_path, exist_ok=True)
            rel_path = os.path.relpath(full_path, Config.get_create_dir())
            print(green(f"[Created folder: {rel_path}]"))
            return True
        except Exception as e:
            print(red(f"[Failed to create folder: {path} - {e}]"))
            return False
    
    @staticmethod
    def list_files(path: str = ".") -> str:
        """List files in directory (shows actual filesystem, not just create dir)"""
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
    
    @staticmethod
    def list_created_files() -> str:
        """List files that have been created in output/create/"""
        create_dir = Config.get_create_dir()
        try:
            if not os.path.exists(create_dir):
                return "No files created yet"
            
            items = os.listdir(create_dir)
            files = [f for f in items if os.path.isfile(os.path.join(create_dir, f))]
            dirs = [d for d in items if os.path.isdir(os.path.join(create_dir, d))]
            
            result = f"Created files in: {create_dir}\n\n"
            if dirs:
                result += "Folders:\n" + "\n".join(f"  [DIR] {d}" for d in dirs[:10]) + "\n\n"
            if files:
                result += "Files:\n" + "\n".join(f"  [FILE] {f}" for f in files[:20])
            if len(files) > 20:
                result += f"\n  ... and {len(files) - 20} more"
            
            return result
        except Exception as e:
            return f"Error: {e}"
    
    @staticmethod
    def read_file(filepath: str) -> str:
        """Read file content (from actual filesystem)"""
        try:
            full_path = filepath
            # Also check in create directory if not found
            if not os.path.exists(full_path):
                alt_path = os.path.join(Config.get_create_dir(), os.path.basename(filepath))
                if os.path.exists(alt_path):
                    full_path = alt_path
            
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            print(green(f"[Read: {full_path} ({len(content)} bytes)]"))
            return content
        except Exception as e:
            print(red(f"[Read failed: {e}]"))
            return None
    
    @staticmethod
    def clear_created_files():
        """Clear all created files (dangerous, asks confirmation)"""
        create_dir = Config.get_create_dir()
        confirm = input(cyan(f"Delete all files in {create_dir}? (y/N): "))
        if confirm.lower() == 'y':
            shutil.rmtree(create_dir)
            os.makedirs(create_dir, exist_ok=True)
            print(green("[All created files cleared]"))
            return True
        return False