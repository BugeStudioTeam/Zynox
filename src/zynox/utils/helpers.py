"""Helper utilities"""

import os
import subprocess

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

def get_install_command(package_manager: str, package: str) -> str:
    """Get install command based on package manager"""
    if package_manager == "pkg":
        return f"pkg install -y {package}"
    elif package_manager == "apt":
        return f"sudo apt install -y {package}"
    elif package_manager == "yum":
        return f"sudo yum install -y {package}"
    elif package_manager == "dnf":
        return f"sudo dnf install -y {package}"
    elif package_manager == "pacman":
        return f"sudo pacman -S --noconfirm {package}"
    elif package_manager == "brew":
        return f"brew install {package}"
    else:
        return None