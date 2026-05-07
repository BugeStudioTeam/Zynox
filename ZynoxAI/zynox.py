#!/usr/bin/env python3
"""
ZynoxAI - AI-powered file/folder creation tool
Supports: GPT, Grok, DeepSeek
"""

import os
import sys
import json
import argparse
import requests
from pathlib import Path
from colorama import init, Fore, Style
import re

# Initialize colorama for cross-platform colored output
init(autoreset=True)

# Configuration
CONFIG_DIR = os.path.expanduser("~/.zynoxai")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")
API_ENDPOINTS = {
    "openai": {
        "url": "https://api.openai.com/v1/chat/completions",
        "models": ["gpt-3.5-turbo", "gpt-4o-mini", "gpt-4o"]
    },
    "grok": {
        "url": "https://api.x.ai/v1/chat/completions",
        "models": ["grok-beta", "grok-2-1212", "grok-2-vision-1212"]
    },
    "deepseek": {
        "url": "https://api.deepseek.com/v1/chat/completions",
        "models": ["deepseek-chat", "deepseek-coder"]
    }
}

def print_logo():
    """Print ZYNOX ASCII logo"""
    logo = f"""
{Fore.CYAN}╔═══════════════════════════════════════════════════════════════╗
{Fore.CYAN}║{Fore.YELLOW}   ███████╗██╗   ██╗███╗   ██╗ ██████╗ ██╗  ██╗{Fore.CYAN}                ║
{Fore.CYAN}║{Fore.YELLOW}   ╚══███╔╝╚██╗ ██╔╝████╗  ██║██╔═══██╗╚██╗██╔╝{Fore.CYAN}                ║
{Fore.CYAN}║{Fore.YELLOW}     ███╔╝  ╚████╔╝ ██╔██╗ ██║██║   ██║ ╚███╔╝ {Fore.CYAN}                ║
{Fore.CYAN}║{Fore.YELLOW}    ███╔╝    ╚██╔╝  ██║╚██╗██║██║   ██║ ██╔██╗ {Fore.CYAN}                ║
{Fore.CYAN}║{Fore.YELLOW}   ███████╗   ██║   ██║ ╚████║╚██████╔╝██╔╝ ██╗{Fore.CYAN}                ║
{Fore.CYAN}║{Fore.YELLOW}   ╚══════╝   ╚═╝   ╚═╝  ╚═══╝ ╚═════╝ ╚═╝  ╚═╝{Fore.CYAN}                ║
{Fore.CYAN}╠═══════════════════════════════════════════════════════════════╣
{Fore.CYAN}║{Fore.GREEN}         AI-Powered File & Folder Creation Tool{Fore.CYAN}                ║
{Fore.CYAN}║{Fore.MAGENTA}              GPT • Grok • DeepSeek{Fore.CYAN}                            ║
{Fore.CYAN}╚═══════════════════════════════════════════════════════════════╝{Style.RESET_ALL}
"""
    print(logo)

class ZynoxAI:
    def __init__(self):
        self.config = self.load_config()
        self.current_provider = self.config.get("default_provider", "openai")

    def load_config(self):
        """Load configuration from file"""
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    return json.load(f)
            except:
                return {
                    "api_keys": {},
                    "default_provider": "openai",
                    "default_model": None
                }
        return {
            "api_keys": {},
            "default_provider": "openai",
            "default_model": None
        }

    def save_config(self):
        """Save configuration to file"""
        os.makedirs(CONFIG_DIR, exist_ok=True)
        with open(CONFIG_FILE, 'w') as f:
            json.dump(self.config, f, indent=2)
        print(f"{Fore.GREEN}✓ Configuration saved")

    def set_api_key(self, provider: str, api_key: str):
        """Set API key for a provider"""
        provider = provider.lower()
        if provider not in API_ENDPOINTS:
            print(f"{Fore.RED}✗ Unsupported provider. Available: {', '.join(API_ENDPOINTS.keys())}")
            return False
        
        self.config["api_keys"][provider] = api_key
        self.save_config()
        print(f"{Fore.GREEN}✓ API key for {provider} configured")
        return True

    def set_default_provider(self, provider: str):
        """Set default provider"""
        provider = provider.lower()
        if provider not in API_ENDPOINTS:
            print(f"{Fore.RED}✗ Unsupported provider. Available: {', '.join(API_ENDPOINTS.keys())}")
            return False
        
        self.config["default_provider"] = provider
        self.save_config()
        print(f"{Fore.GREEN}✓ Default provider set to {provider}")
        self.current_provider = provider
        return True

    def create_prompt(self, user_input: str) -> str:
        """Create a prompt for the AI"""
        return f"""You are ZynoxAI, a file/folder creation assistant. Based on the user's request, generate a JSON response with actions to create files or folders.

Rules:
1. ONLY output valid JSON, no other text.
2. For folders: {{"type": "folder", "path": "folder_name"}}
3. For files: {{"type": "file", "path": "file_name", "content": "file_content_here"}}
4. If multiple items: {{"actions": [action1, action2, ...]}}
5. Use appropriate file extensions (.py, .txt, .js, .html, .json, etc.)
6. For code files, provide meaningful code content
7. Paths can include nested directories (e.g., "src/main.py")
8. Use forward slashes for paths

User request: {user_input}

Response format zynox:
- Single file: {{"type": "file", "path": "hello.py", "content": "print('Hello World')\\n"}}
- Single folder: {{"type": "folder", "path": "my_project"}}
- Multiple: {{"actions": [{{"type": "folder", "path": "src"}}, {{"type": "file", "path": "src/main.py", "content": "# Main file"}}]}}

Generate JSON response:"""

    def call_api(self, provider: str, prompt: str, model: str = None) -> str:
        """Call the specified AI provider API"""
        if provider not in self.config["api_keys"] or not self.config["api_keys"][provider]:
            print(f"{Fore.RED}✗ API key not set for {provider}. Use 'zynox set-key {provider} YOUR_KEY'")
            return None
        
        api_key = self.config["api_keys"][provider]
        endpoint_config = API_ENDPOINTS[provider]
        
        # Select model
        if not model:
            model = self.config.get("default_model", endpoint_config["models"][0])
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        # Build payload based on provider
        if provider == "deepseek":
            # DeepSeek specific payload (no stream parameter)
            payload = {
                "model": model,
                "messages": [
                    {"role": "system", "content": "You are a JSON output generator. Always output pure JSON without markdown formatting."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.1,
                "max_tokens": 16000
            }
        elif provider == "grok":
            # Grok/xAI specific payload
            payload = {
                "model": model,
                "messages": [
                    {"role": "system", "content": "You are a JSON output generator. Always output pure JSON without markdown formatting."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.3,
                "max_tokens": 8192
            }
        else:
            # OpenAI standard payload
            payload = {
                "model": model,
                "messages": [
                    {"role": "system", "content": "You are a JSON output generator. Always output pure JSON without markdown formatting."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.3,
                "max_tokens": 8192
            }
        
        try:
            print(f"{Fore.CYAN}→ Calling {provider.upper()} API (model: {model})...")
            response = requests.post(endpoint_config["url"], headers=headers, json=payload, timeout=180)
            
            # Check for HTTP errors
            if response.status_code != 200:
                print(f"{Fore.RED}✗ HTTP {response.status_code} Error")
                print(f"{Fore.YELLOW}Response: {response.text[:500]}")
                return None
            
            result = response.json()
            ai_response = result["choices"][0]["message"]["content"]
            
            # Clean up response (remove markdown code blocks if present)
            ai_response = re.sub(r'```json\s*', '', ai_response)
            ai_response = re.sub(r'```\s*', '', ai_response)
            ai_response = ai_response.strip()
            
            return ai_response
            
        except requests.exceptions.Timeout:
            print(f"{Fore.RED}✗ Request timeout")
            print(f"{Fore.YELLOW}💡 Tip: Try again or use a different provider")
            return None
        except requests.exceptions.RequestException as e:
            print(f"{Fore.RED}✗ API error: {e}")
            return None
        except (KeyError, json.JSONDecodeError) as e:
            print(f"{Fore.RED}✗ Invalid response format: {e}")
            return None

    def parse_and_execute(self, ai_response: str, base_path: str = "."):
        """Parse AI response and execute file/folder creation"""
        try:
            data = json.loads(ai_response)
        except json.JSONDecodeError as e:
            print(f"{Fore.RED}✗ Failed to parse AI response: {e}")
            print(f"{Fore.YELLOW}Raw response: {ai_response[:500]}")
            return False
        
        # Normalize structure
        if "type" in data:
            actions = [data]
        elif "actions" in data:
            actions = data["actions"]
        else:
            print(f"{Fore.RED}✗ Invalid response format - missing 'type' or 'actions'")
            print(f"{Fore.YELLOW}Response: {json.dumps(data, indent=2)[:500]}")
            return False
        
        created = []
        failed = []
        
        for action in actions:
            action_type = action.get("type")
            path = action.get("path")
            
            if not path:
                print(f"{Fore.YELLOW}⚠ Skipping action without path")
                continue
            
            full_path = os.path.join(base_path, path)
            
            if action_type == "folder":
                try:
                    os.makedirs(full_path, exist_ok=True)
                    print(f"{Fore.GREEN}✓ Created folder: {path}")
                    created.append(path)
                except OSError as e:
                    print(f"{Fore.RED}✗ Failed to create folder {path}: {e}")
                    failed.append(path)
                    
            elif action_type == "file":
                try:
                    # Create parent directories if needed
                    parent_dir = os.path.dirname(full_path)
                    if parent_dir:
                        os.makedirs(parent_dir, exist_ok=True)
                    
                    content = action.get("content", "")
                    with open(full_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    file_size = len(content)
                    print(f"{Fore.GREEN}✓ Created file: {path} ({file_size} bytes)")
                    created.append(path)
                except OSError as e:
                    print(f"{Fore.RED}✗ Failed to create file {path}: {e}")
                    failed.append(path)
            else:
                print(f"{Fore.YELLOW}⚠ Unknown action type: {action_type}")
        
        print(f"\n{Fore.CYAN}Summary: {len(created)} created, {len(failed)} failed")
        if created:
            print(f"{Fore.GREEN}Created items:")
            for item in created:
                print(f"  - {item}")
        
        return len(failed) == 0

    def run(self, user_input: str, provider: str = None, model: str = None, base_path: str = "."):
        """Main execution flow"""
        if not user_input:
            print(f"{Fore.RED}✗ No input provided")
            return False
        
        # Determine provider
        target_provider = provider or self.config.get("default_provider", "openai")
        
        # Create prompt
        prompt = self.create_prompt(user_input)
        
        # Call API
        ai_response = self.call_api(target_provider, prompt, model)
        if not ai_response:
            return False
        
        # Show response preview
        print(f"{Fore.MAGENTA}→ AI Response Preview: {ai_response[:200]}...")
        
        # Execute actions
        return self.parse_and_execute(ai_response, base_path)

def main():
    parser = argparse.ArgumentParser(
        description="ZynoxAI - AI-powered file/folder creation tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  zynox set-key openai sk-xxx
  zynox set-default deepseek
  zynox "create a python file called main.py with hello world"
  zynox -p grok "make a folder called my_project"
  zynox -d ./workspace "create an index.html file"
  zynox --list-models
  zynox --show-config
        """
    )
    
    # Configuration commands
    parser.add_argument("--set-key", metavar="PROVIDER", help="Set API key for provider (openai/grok/deepseek)")
    parser.add_argument("--key", help="API key value")
    parser.add_argument("--set-default", metavar="PROVIDER", help="Set default provider")
    
    # Execution options
    parser.add_argument("input", nargs="?", help="User request for file/folder creation")
    parser.add_argument("-p", "--provider", choices=["openai", "grok", "deepseek"], help="AI provider to use")
    parser.add_argument("-m", "--model", help="Specific model to use")
    parser.add_argument("-d", "--dir", help="Base directory for creation (default: current)", default=".")
    parser.add_argument("--list-models", action="store_true", help="List available models")
    parser.add_argument("--show-config", action="store_true", help="Show current configuration")
    
    args = parser.parse_args()
    
    # only zynox
    show_logo = False
    if len(sys.argv) == 1:
        show_logo = True
    elif len(sys.argv) == 2 and sys.argv[1] in ["--help", "-h"]:
        # 
        show_logo = False
    else:
        # 
        show_logo = False
    
    if show_logo:
        print_logo()
    
    # Initialize tool
    zynox = ZynoxAI()
    
    # Handle configuration commands
    if args.set_key:
        if not args.key:
            print(f"{Fore.RED}✗ Please provide API key with --key")
            sys.exit(1)
        zynox.set_api_key(args.set_key, args.key)
        sys.exit(0)
    
    if args.set_default:
        zynox.set_default_provider(args.set_default)
        sys.exit(0)
    
    if args.list_models:
        print(f"\n{Fore.CYAN}Available Models:")
        for provider, info in API_ENDPOINTS.items():
            print(f"\n{Fore.GREEN}{provider.upper()}:")
            for model in info["models"]:
                print(f"  - {model}")
        sys.exit(0)
    
    if args.show_config:
        print(f"\n{Fore.CYAN}Current Configuration:")
        print(f"  Default Provider: {zynox.config.get('default_provider', 'Not set')}")
        print(f"  Default Model: {zynox.config.get('default_model', 'Not set')}")
        print(f"  Configured APIs: {', '.join(zynox.config.get('api_keys', {}).keys())}")
        sys.exit(0)
    
    # Execute main command
    if not args.input:
        parser.print_help()
        sys.exit(1)
    
    success = zynox.run(args.input, args.provider, args.model, args.dir)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()