"""Command line interface for ZynoxAI"""

import sys
import os
import json
import argparse
import re
from pathlib import Path

from .config import Config
from .utils.colors import print_logo, green, red, yellow, cyan, magenta
from .utils.helpers import detect_environment, get_package_manager
from .memory.session import SessionManager
from .core.ai_providers.factory import AIProviderFactory
from .core.prompt.builder import PromptBuilder
from .core.command.executor import CommandExecutor
from .core.file.manager import FileManager
from .core.file.search import FileSearcher
from .bot.telegram import TelegramBot

class ZynoxAI:
    """Main ZynoxAI application"""
    
    def __init__(self):
        self.config = Config()
        self.session_manager = SessionManager()
        self.command_executor = CommandExecutor()
        self.file_manager = FileManager()
        self.file_searcher = FileSearcher()
        self.current_provider = self.config.get_default_provider()
        self.task_complete = False
    
    def process_request(self, user_input: str, base_path: str = ".") -> bool:
        """Process a user request"""
        if not user_input:
            return False
        
        # Show where files will be created
        print(cyan(f"[Files will be created in: {Config.get_create_dir()}]"))
        
        # Check for file search patterns
        search_pattern = re.search(r'find\s+[\'"]?([^\'"]+\.(?:html|css|js|py|json|yml|yaml|txt|md))[\'"]?', user_input, re.IGNORECASE)
        
        context = ""
        if search_pattern:
            filename = search_pattern.group(1)
            found_file = self.file_searcher.find_file(filename, base_path)
            if found_file:
                file_content = self.file_manager.read_file(found_file)
                if file_content:
                    context = file_content
                    print(green(f"✓ Using '{filename}' as reference\n"))
        
        # Build prompt
        file_list = self.file_manager.list_files(base_path)
        prompt = PromptBuilder.create_prompt(user_input, context, file_list)
        
        # Call AI
        api_key = self.config.get_api_key(self.current_provider)
        if not api_key:
            print(red(f"[No API key for {self.current_provider}]"))
            return False
        
        provider = AIProviderFactory.create(self.current_provider, api_key)
        default_model = self.config.get_default_model()
        
        try:
            print(cyan("[Thinking...]"))
            ai_response = provider.call(prompt, default_model)
            
            # Parse and execute
            return self.parse_and_execute(ai_response, base_path)
        except Exception as e:
            print(red(f"[Error: {e}]"))
            return False
    
    def parse_and_execute(self, ai_response: str, base_path: str = ".") -> bool:
        """Parse AI response and execute actions"""
        try:
            data = json.loads(ai_response)
        except:
            match = re.search(r'\{.*\}', ai_response, re.DOTALL)
            if match:
                try:
                    data = json.loads(match.group())
                except:
                    print(red("[Invalid JSON]"))
                    return False
            else:
                print(red("[Invalid response]"))
                return False
        
        if "type" in data:
            actions = [data]
        elif "actions" in data:
            actions = data["actions"]
        else:
            return False
        
        for action in actions:
            t = action.get("type")
            
            if t == "search_file":
                self.file_searcher.find_file(action.get("filename"), base_path)
            elif t == "search_folder":
                self.file_searcher.find_folder(action.get("foldername"), base_path)
            elif t == "read":
                path = action.get("path")
                if path:
                    content = self.file_manager.read_file(path)
                    if content:
                        print(f"\n{cyan('='*50)}\n{content[:1000]}\n{cyan('='*50)}\n")
            elif t == "list":
                print(f"\n{cyan(self.file_manager.list_files(action.get('path', base_path)))}\n")
            elif t == "command":
                stdout, stderr = self.command_executor.execute(action.get("command"))
                if stdout:
                    print(stdout[:500])
            elif t == "file":
                # Files are automatically created in output/create/
                self.file_manager.create_file(action.get("path"), action.get("content", ""), base_path)
            elif t == "folder":
                # Folders are automatically created in output/create/
                self.file_manager.create_folder(action.get("path"), base_path)
            elif t == "complete":
                print(green(f"[Done: {action.get('message', 'Complete')}]"))
                self.task_complete = True
                return True
        
        return True
    
    def run(self, user_input: str, provider: str = None, model: str = None, base_path: str = "."):
        """Main execution"""
        if provider:
            self.current_provider = provider
        if model:
            self.config.set_default_model(model)
        
        self.session_manager.add_message("user", user_input)
        self.task_complete = False
        
        success = self.process_request(user_input, base_path)
        
        if success:
            self.session_manager.add_message("assistant", "Task completed")
        
        return success

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="ZynoxAI - AI-powered file/folder creation tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  zynox --set-key openai --key sk-xxx
  zynox --set-key gemini --key AIzaSyxxx
  zynox --set-default deepseek
  zynox "create a python file called main.py with hello world"
  zynox -p grok "make a folder called my_project"
  zynox -d ./workspace "create an index.html file"
  zynox --list-models
  zynox --show-config
  zynox --new-session
  zynox --list-sessions
  zynox --clear-memory
  zynox --list-created
  zynox --clear-created
  zynox --telegram-bot YOUR_TOKEN

Note: All created files are saved in ~/ZynoxAI/output/create/
        """
    )
    
    # Memory commands
    parser.add_argument("--new-session", action="store_true", help="Start new conversation")
    parser.add_argument("--list-sessions", action="store_true", help="List all sessions")
    parser.add_argument("--load-session", metavar="ID", help="Load a session")
    parser.add_argument("--delete-session", metavar="ID", help="Delete a session")
    parser.add_argument("--clear-memory", action="store_true", help="Clear current memory")
    
    # File management commands
    parser.add_argument("--list-created", action="store_true", help="List all created files")
    parser.add_argument("--clear-created", action="store_true", help="Clear all created files")
    
    # Config commands
    parser.add_argument("--set-key", metavar="PROVIDER", help="Set API key (openai/gemini/grok/deepseek)")
    parser.add_argument("--key", help="API key value")
    parser.add_argument("--set-default", metavar="PROVIDER", help="Set default provider")
    parser.add_argument("--show-config", action="store_true", help="Show configuration")
    parser.add_argument("--list-models", action="store_true", help="List models")
    
    # Telegram bot
    parser.add_argument("--telegram-bot", metavar="TOKEN", help="Start Telegram bot")
    
    # Execution options
    parser.add_argument("input", nargs="?", help="Your request")
    parser.add_argument("-p", "--provider", choices=["openai", "gemini", "grok", "deepseek"], help="AI provider")
    parser.add_argument("-m", "--model", help="Specific model")
    parser.add_argument("-d", "--dir", help="Working directory", default=".")
    
    args = parser.parse_args()
    
    # Show logo only when no arguments
    if len(sys.argv) == 1:
        print_logo()
    
    zynox = ZynoxAI()
    config = Config()
    session = SessionManager()
    file_manager = FileManager()
    
    # Handle Telegram bot (runs separately)
    if args.telegram_bot:
        bot = TelegramBot(zynox, args.telegram_bot)
        print(green("[Telegram Bot running. Press Ctrl+C to stop]"))
        try:
            bot.run()
        except KeyboardInterrupt:
            print(yellow("[Bot stopped]"))
        sys.exit(0)
    
    # Handle file management commands
    if args.list_created:
        print(file_manager.list_created_files())
        sys.exit(0)
    if args.clear_created:
        file_manager.clear_created_files()
        sys.exit(0)
    
    # Handle memory commands
    if args.new_session:
        session.new_session()
        sys.exit(0)
    if args.list_sessions:
        sessions = session.list_sessions()
        if sessions:
            for s in sessions:
                print(f"  {s['id']} - {s['message_count']} msgs - {s['created'][:19]}")
        else:
            print("[No sessions]")
        sys.exit(0)
    if args.load_session:
        if session.load_session(args.load_session):
            print(green(f"[Loaded session: {args.load_session}]"))
        else:
            print(red(f"[Session not found: {args.load_session}]"))
        sys.exit(0)
    if args.delete_session:
        if session.delete_session(args.delete_session):
            print(green(f"[Deleted session: {args.delete_session}]"))
        else:
            print(red(f"[Session not found: {args.delete_session}]"))
        sys.exit(0)
    if args.clear_memory:
        session.clear_memory()
        print(green("[Memory cleared]"))
        sys.exit(0)
    
    # Handle config commands
    if args.set_key:
        if not args.key:
            print(red("[Need --key]"))
            sys.exit(1)
        config.set_api_key(args.set_key, args.key)
        print(green(f"[API key for {args.set_key} configured]"))
        sys.exit(0)
    if args.set_default:
        config.set_default_provider(args.set_default)
        print(green(f"[Default provider set to {args.set_default}]"))
        sys.exit(0)
    if args.list_models:
        from .core.ai_providers.factory import AIProviderFactory
        for p in AIProviderFactory.get_available_providers():
            print(f"\n{p.upper()}:")
            if p == "openai":
                print("  - gpt-3.5-turbo\n  - gpt-4o-mini\n  - gpt-4o")
            elif p == "gemini":
                print("  - gemini-1.5-flash\n  - gemini-1.5-pro\n  - gemini-2.0-flash-exp")
            elif p == "grok":
                print("  - grok-beta\n  - grok-2-1212\n  - grok-2-vision-1212")
            elif p == "deepseek":
                print("  - deepseek-chat\n  - deepseek-coder")
        sys.exit(0)
    if args.show_config:
        print(f"Default Provider: {config.get_default_provider()}")
        print(f"Default Model: {config.get_default_model() or 'Not set'}")
        print(f"API Keys: {', '.join(config.data.get('api_keys', {}).keys())}")
        print(f"Environment: {detect_environment().upper()}")
        print(f"Package Manager: {get_package_manager()}")
        print(f"Created Files Directory: {Config.get_create_dir()}")
        sys.exit(0)
    
    # Execute main command
    if not args.input:
        parser.print_help()
        sys.exit(1)
    
    success = zynox.run(args.input, args.provider, args.model, args.dir)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()