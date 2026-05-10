"""Configuration management for ZynoxAI"""

import os
import json
from pathlib import Path

# Base directories
BASE_DIR = os.path.expanduser("~/ZynoxAI")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
CREATE_DIR = os.path.join(OUTPUT_DIR, "create")  # 新增：创建文件的目录
CONFIG_DIR = os.path.expanduser("~/.zynoxai")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")
MEMORY_DIR = os.path.join(CONFIG_DIR, "memories")
TELEGRAM_CONFIG_FILE = os.path.join(CONFIG_DIR, "telegram_config.json")

# Create directories
os.makedirs(CREATE_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(CONFIG_DIR, exist_ok=True)
os.makedirs(MEMORY_DIR, exist_ok=True)
os.makedirs(os.path.join(OUTPUT_DIR, "logs"), exist_ok=True)
os.makedirs(os.path.join(OUTPUT_DIR, "cache"), exist_ok=True)
os.makedirs(os.path.join(OUTPUT_DIR, "temp"), exist_ok=True)

class Config:
    """Configuration manager"""
    
    def __init__(self):
        self.data = self.load()
    
    def load(self):
        """Load configuration from file"""
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {
            "api_keys": {},
            "default_provider": "openai",
            "default_model": None
        }
    
    def save(self):
        """Save configuration to file"""
        with open(CONFIG_FILE, 'w') as f:
            json.dump(self.data, f, indent=2)
        print(f"[Configuration saved]")
    
    def get_api_key(self, provider: str) -> str:
        """Get API key for a provider"""
        return self.data.get("api_keys", {}).get(provider.lower())
    
    def set_api_key(self, provider: str, key: str):
        """Set API key for a provider"""
        provider = provider.lower()
        if "api_keys" not in self.data:
            self.data["api_keys"] = {}
        self.data["api_keys"][provider] = key
        self.save()
    
    def get_default_provider(self) -> str:
        """Get default provider"""
        return self.data.get("default_provider", "openai")
    
    def set_default_provider(self, provider: str):
        """Set default provider"""
        self.data["default_provider"] = provider.lower()
        self.save()
    
    def get_default_model(self) -> str:
        """Get default model"""
        return self.data.get("default_model")
    
    def set_default_model(self, model: str):
        """Set default model"""
        self.data["default_model"] = model
        self.save()
    
    @staticmethod
    def get_create_dir() -> str:
        """Get the directory where files should be created"""
        return CREATE_DIR