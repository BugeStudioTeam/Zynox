"""Smart installer for missing packages"""

import subprocess
import os
from ...constants import PACKAGE_MAP
from ...utils.helpers import detect_environment, get_package_manager, get_install_command
from ...utils.colors import green, red, yellow, cyan
from ...config import Config

class SmartInstaller:
    """Smart installation of missing packages"""
    
    def __init__(self):
        self.environment = detect_environment()
        self.package_manager = get_package_manager()
        self.package_cache = {}
        self.create_dir = Config.get_create_dir()
    
    def is_installed(self, cmd_name: str) -> bool:
        """Check if a command is already installed"""
        if cmd_name in self.package_cache:
            return self.package_cache[cmd_name]
        
        result = subprocess.run(f'which {cmd_name}', shell=True, capture_output=True, text=True)
        if result.returncode == 0 and result.stdout.strip():
            self.package_cache[cmd_name] = True
            return True
        
        result = subprocess.run(f'{cmd_name} --version', shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            self.package_cache[cmd_name] = True
            return True
        
        self.package_cache[cmd_name] = False
        return False
    
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
            print(cyan(f"[Trying: {url}]"))
            download_cmd = f"wget -O {jar_path} {url} --timeout=10"
            result = subprocess.run(download_cmd, shell=True, capture_output=True)
            if result.returncode == 0 and os.path.exists(jar_path) and os.path.getsize(jar_path) > 1000:
                print(green("[Downloaded apktool.jar]"))
                break
        else:
            print(red("[Failed to download apktool.jar]"))
            return False
        
        script_path = os.path.join(prefix, "bin/apktool")
        script_content = f'''#!/bin/bash
java -jar "{jar_path}" "$@"
'''
        with open(script_path, 'w') as f:
            f.write(script_content)
        os.chmod(script_path, 0o755)
        
        print(green("[apktool installed successfully]"))
        self.package_cache['apktool'] = True
        return True
    
    def install(self, cmd_name: str) -> bool:
        """Install a package"""
        # Special handling for apktool
        if cmd_name == 'apktool':
            return self.install_apktool()
        
        if cmd_name not in PACKAGE_MAP:
            return False
        
        package = PACKAGE_MAP[cmd_name]
        print(yellow(f"[Package '{package}' required for '{cmd_name}']"))
        
        confirm = input(cyan(f"Install '{package}'? (y/N): "))
        if confirm.lower() != 'y':
            return False
        
        install_cmd = get_install_command(self.package_manager, package)
        if not install_cmd:
            return False
        
        result = subprocess.run(install_cmd, shell=True, capture_output=True)
        if result.returncode == 0:
            print(green(f"[Installed {package}]"))
            self.package_cache[cmd_name] = True
            return True
        
        return False