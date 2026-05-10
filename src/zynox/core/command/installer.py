"""Smart installer for missing packages"""

import subprocess
import os
from ...utils.helpers import detect_environment, get_package_manager
from ...utils.colors import green, red, yellow, cyan
from ...config import OUTPUT_DIR

class SmartInstaller:
    """Smart installation of missing packages"""
    
    def __init__(self):
        self.environment = detect_environment()
        self.package_manager = get_package_manager()
    
    def get_install_command(self, package: str) -> str:
        """Get install command based on environment"""
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
        return None
    
    def install_apktool(self) -> bool:
        """Install apktool from source"""
        print(cyan("[Installing apktool...]"))
        
        urls = [
            "https://raw.githubusercontent.com/iBotPeaches/Apktool/master/scripts/linux/apktool.jar",
            "https://github.com/iBotPeaches/Apktool/releases/latest/download/apktool.jar",
        ]
        
        prefix = os.environ.get('PREFIX', '/usr/local')
        jar_path = os.path.join(prefix, "share/apktool/apktool.jar")
        os.makedirs(os.path.dirname(jar_path), exist_ok=True)
        
        for url in urls:
            download_cmd = f"wget -O {jar_path} {url} --timeout=10"
            result = subprocess.run(download_cmd, shell=True, capture_output=True)
            if result.returncode == 0 and os.path.exists(jar_path) and os.path.getsize(jar_path) > 1000:
                break
        else:
            return False
        
        script_path = os.path.join(prefix, "bin/apktool")
        script_content = f'''#!/bin/bash
java -jar "{jar_path}" "$@"
'''
        with open(script_path, 'w') as f:
            f.write(script_content)
        os.chmod(script_path, 0o755)
        
        print(green("[apktool installed successfully]"))
        return True
    
    def install(self, cmd_name: str) -> bool:
        """Install a package"""
        packages = {
            'zip': 'zip', 'unzip': 'unzip', 'tar': 'tar', 'git': 'git',
            'curl': 'curl', 'wget': 'wget', 'ffmpeg': 'ffmpeg',
            'java': 'openjdk-17', 'gcc': 'gcc', 'make': 'make',
        }
        
        if cmd_name == 'apktool':
            return self.install_apktool()
        
        if cmd_name not in packages:
            return False
        
        package = packages[cmd_name]
        print(yellow(f"[Package '{package}' required for '{cmd_name}']"))
        
        confirm = input(cyan(f"Install '{package}'? (y/N): "))
        if confirm.lower() != 'y':
            return False
        
        install_cmd = self.get_install_command(package)
        if not install_cmd:
            return False
        
        result = subprocess.run(install_cmd, shell=True, capture_output=True)
        if result.returncode == 0:
            print(green(f"[Installed {package}]"))
            return True
        return False