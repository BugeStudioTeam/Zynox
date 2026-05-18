"""Step-by-step task executor with streaming output and duplicate detection"""

import json
import re
import sys
import time
import threading
from typing import Callable, Optional
from ...utils.colors import green, red, yellow, cyan, magenta

class StepExecutor:
    """Execute tasks step by step with streaming output"""
    
    def __init__(self, zynox_instance, output_callback: Optional[Callable] = None):
        self.zynox = zynox_instance
        self.output_callback = output_callback
        self.step_number = 0
        self.history = []
        self.max_steps = 30
        self.last_actions = []
        self.completed_tasks = set()
    
    def emit(self, text: str, color: str = "white"):
        """Emit output through callback or print"""
        plain_text = text
        if self.output_callback:
            self.output_callback(plain_text + "\n", color)
        else:
            if color == "green":
                print(green(text))
            elif color == "red":
                print(red(text))
            elif color == "yellow":
                print(yellow(text))
            elif color == "cyan":
                print(cyan(text))
            elif color == "magenta":
                print(magenta(text))
            else:
                print(text)
    
    def emit_step(self, action: dict):
        """Emit step information"""
        self.step_number += 1
        action_type = action.get("type", "unknown")
        
        self.emit(f"\n{'='*50}", "cyan")
        self.emit(f"Step {self.step_number}: {action_type}", "magenta")
        self.emit(f"{'='*50}", "cyan")
        
        if action_type == "command" or action_type == "execute":
            self.emit(f"→ Command: {action.get('command', '')}", "cyan")
        elif action_type == "search_file":
            self.emit(f"→ Searching for: {action.get('filename', '')}", "cyan")
        elif action_type == "read":
            self.emit(f"→ Reading: {action.get('path', '')}", "cyan")
        elif action_type == "create_file":
            self.emit(f"→ Creating file: {action.get('path', '')}", "cyan")
        elif action_type == "create_folder":
            self.emit(f"→ Creating folder: {action.get('path', '')}", "cyan")
    
    def emit_result(self, result: str, success: bool):
        """Emit action result"""
        status = "SUCCESS" if success else "FAILED"
        color = "green" if success else "red"
        self.emit(f"\nResult: {status}", color)
        if result and len(result) < 500:
            self.emit(result[:500], "white")
        elif result:
            self.emit(result[:200] + "... (truncated)", "white")
    
    def execute_action(self, action: dict, base_path: str = ".") -> tuple:
        """Execute a single action and return result"""
        action_type = action.get("type")
        
        if action_type == "command" or action_type == "execute":
            cmd = action.get("command")
            if cmd:
                self.emit(f"\n[Executing] {cmd}", "cyan")
                stdout, stderr = self.zynox.command_executor.execute(cmd)
                output = stdout if stdout else stderr if stderr else ""
                success = stdout is not None or stderr is not None
                return output, success
        
        elif action_type == "search_file":
            filename = action.get("filename")
            if filename:
                result = self.zynox.file_searcher.find_file(filename, base_path)
                if result:
                    return f"Found: {result}", True
                return f"File not found: {filename}", False
        
        elif action_type == "search_folder":
            foldername = action.get("foldername")
            if foldername:
                result = self.zynox.file_searcher.find_folder(foldername, base_path)
                if result:
                    return f"Found folder: {result}", True
                return f"Folder not found: {foldername}", False
        
        elif action_type == "read":
            path = action.get("path")
            if path:
                content = self.zynox.file_manager.read_file(path)
                if content:
                    preview = content[:500] + ("..." if len(content) > 500 else "")
                    return f"File content:\n{preview}", True
                return f"Failed to read: {path}", False
        
        elif action_type == "list":
            path = action.get("path", base_path)
            files = self.zynox.file_manager.list_files(path)
            return files, True if files else False
        
        elif action_type == "create_file":
            path = action.get("path")
            content = action.get("content", "")
            if path:
                success = self.zynox.file_manager.create_file(path, content, base_path)
                task_key = f"file:{path}"
                self.completed_tasks.add(task_key)
                return f"File created: {path}", success
            return "No path specified", False
        
        elif action_type == "create_folder":
            path = action.get("path")
            if path:
                success = self.zynox.file_manager.create_folder(path, base_path)
                task_key = f"folder:{path}"
                self.completed_tasks.add(task_key)
                return f"Folder created: {path}", success
            return "No path specified", False
        
        elif action_type == "complete":
            return action.get("message", "Task completed"), True
        
        else:
            return f"Unknown action type: {action_type}", False
        
        return "No action executed", False
    
    def is_repeating(self, action: dict) -> bool:
        """Check if we're stuck in a loop repeating the same action"""
        if not action:
            return False
        
        action_type = action.get("type", "")
        if action_type == "create_folder":
            signature = f"{action_type}:{action.get('path', '')}"
        elif action_type == "create_file":
            signature = f"{action_type}:{action.get('path', '')}"
        else:
            signature = f"{action_type}"
        
        # Check if this action was already completed
        if action_type == "create_folder":
            task_key = f"folder:{action.get('path', '')}"
            if task_key in self.completed_tasks:
                self.emit(f"⚠ Task '{action.get('path', '')}' already completed, skipping", "yellow")
                return True
        
        if action_type == "create_file":
            task_key = f"file:{action.get('path', '')}"
            if task_key in self.completed_tasks:
                self.emit(f"⚠ File '{action.get('path', '')}' already created, skipping", "yellow")
                return True
        
        self.last_actions.append(signature)
        if len(self.last_actions) > 5:
            self.last_actions.pop(0)
        
        if len(self.last_actions) >= 3 and all(x == signature for x in self.last_actions[-3:]):
            self.emit(f"⚠ Detected loop: repeating '{signature}'", "yellow")
            return True
        
        return False
    
    def call_ai(self, prompt: str) -> Optional[str]:
        """Call AI and get response"""
        try:
            response = self.zynox.call_api(self.zynox.current_provider, prompt)
            return response
        except Exception as e:
            self.emit(f"AI call failed: {e}", "red")
            return None
    
    def parse_action(self, response: str) -> Optional[dict]:
        """Parse AI response into action dict"""
        if not response:
            return None
        
        if "complete" in response.lower():
            match = re.search(r'"message":\s*"([^"]+)"', response)
            message = match.group(1) if match else "Task completed"
            return {"type": "complete", "message": message}
        
        patterns = [
            r'\{[^{}]*"type"\s*:\s*"[^"]+"[^{}]*\}',
            r'\{\s*"type"\s*:\s*"[^"]+",\s*"[^"]+"\s*:\s*"[^"]*"\s*\}',
            r'\{"type":\s*"[^"]+",\s*"[^"]+":\s*"[^"]*"\}'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, response, re.DOTALL)
            if match:
                try:
                    action = json.loads(match.group())
                    if "type" in action:
                        return action
                except:
                    pass
        
        try:
            action = json.loads(response)
            if "type" in action:
                return action
        except:
            pass
        
        return None
    
    def run(self, user_input: str, base_path: str = ".") -> bool:
        """Run task with step-by-step execution"""
        self.step_number = 0
        self.history = []
        self.last_actions = []
        self.completed_tasks = set()
        
        self.emit("\n" + "="*60, "cyan")
        self.emit("ZynoxAI - Step-by-Step Execution Mode", "magenta")
        self.emit("="*60, "cyan")
        self.emit(f"\nTask: {user_input}\n", "white")
        
        file_list = self.zynox.file_manager.list_files(base_path)
        
        from ..prompt.templates import build_initial_prompt
        prompt = build_initial_prompt(user_input, file_list)
        
        step_result = ""
        consecutive_failures = 0
        
        while self.step_number < self.max_steps:
            self.emit(f"\n[AI Thinking...]", "yellow")
            response = self.call_ai(prompt)
            
            if not response:
                self.emit("Failed to get AI response", "red")
                return False
            
            action = self.parse_action(response)
            if not action:
                self.emit(f"Failed to parse AI response: {response[:200]}", "red")
                consecutive_failures += 1
                if consecutive_failures >= 3:
                    self.emit("Too many parse failures, ending task", "yellow")
                    return True
                continue
            else:
                consecutive_failures = 0
            
            if action.get("type") == "complete":
                self.emit(f"\n✓ {action.get('message', 'Task completed')}", "green")
                return True
            
            if self.is_repeating(action):
                self.emit("\n✓ Detected task completion, ending execution", "green")
                return True
            
            self.emit_step(action)
            result, success = self.execute_action(action, base_path)
            self.emit_result(result, success)
            
            self.history.append({
                "step": self.step_number,
                "action": action,
                "result": result,
                "success": success
            })
            
            from ..prompt.templates import build_step_prompt
            step_result = f"Action: {json.dumps(action)}\nResult: {'SUCCESS' if success else 'FAILED'}\nOutput: {result[:1000]}"
            prompt = build_step_prompt(user_input, step_result, "", self.step_number)
            
            if self.step_number >= 10:
                prompt += "\n\nYou have performed many steps. If the task is complete, output COMPLETE."
            
            time.sleep(0.1)
        
        self.emit(f"\n⚠ Max steps ({self.max_steps}) reached. Task may not be complete.", "yellow")
        return True