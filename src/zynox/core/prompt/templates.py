"""Prompt templates for AI with step-by-step execution"""

import os

RULES_FILE = os.path.join(os.path.dirname(__file__), "rules.txt")

def load_rules() -> str:
    """Load execution rules from txt file"""
    try:
        with open(RULES_FILE, 'r') as f:
            return f.read()
    except:
        return """# ZynoxAI Execution Rules
Execute ONE action at a time. After each action, wait for result.
Output ONLY valid JSON with one action.
Complete when task is done.

IMPORTANT: When you have created all requested files/folders, output COMPLETE.
Do NOT repeat the same action multiple times.
Do NOT keep creating folders after they already exist.
"""

def build_step_prompt(user_input: str, step_result: str, context: str, step_number: int) -> str:
    """Build prompt for step-by-step execution"""
    rules = load_rules()
    
    return f"""{rules}

## Current Status
Step: {step_number}
Previous Action Result:
{step_result[:2000] if step_result else "No previous action"}

## Context
{context[:1000] if context else "No additional context"}

## User Request
{user_input}

## Instructions
Based on the previous result, decide the NEXT SINGLE action.
Output ONLY ONE JSON action.

VALID JSON FORMATS (MUST include required fields):
- Create folder: {{"type": "create_folder", "path": "folder_name"}}
- Create file: {{"type": "create_file", "path": "file_name", "content": "file_content"}}
- Execute command: {{"type": "command", "command": "command_string"}}
- Complete: {{"type": "complete", "message": "completion_message"}}

EXAMPLES:
- Create folder: {{"type": "create_folder", "path": "my_folder"}}
- Create file: {{"type": "create_file", "path": "my_folder/hello.txt", "content": "Hello World"}}
- Complete: {{"type": "complete", "message": "All items created"}}

CRITICAL:
- For create_folder, you MUST include "path" field
- For create_file, you MUST include "path" and "content" fields
- Do NOT omit required fields
- Do NOT output empty or malformed JSON

Action:"""

def build_initial_prompt(user_input: str, context: str) -> str:
    """Build initial prompt for first step"""
    rules = load_rules()
    
    return f"""{rules}

## Current Status
This is the first step. No previous actions.

## Context
{context[:1000] if context else "No additional context"}

## User Request
{user_input}

## Instructions
Analyze the request and decide the FIRST action.
Output ONLY ONE JSON action.

VALID JSON FORMATS:
- Create folder: {{"type": "create_folder", "path": "folder_name"}}
- Create file: {{"type": "create_file", "path": "file_name", "content": "file_content"}}
- Execute command: {{"type": "command", "command": "command_string"}}
- Complete: {{"type": "complete", "message": "completion_message"}}

EXAMPLES:
For "create a folder called my_project":
{{"type": "create_folder", "path": "my_project"}}

For "create a python file called hello.py with print('Hello')":
{{"type": "create_file", "path": "hello.py", "content": "print('Hello')\n"}}

For "create a zip file with python files":
First step: {{"type": "command", "command": "find . -name '*.py' -type f"}}

CRITICAL:
- create_folder MUST have "path" field
- create_file MUST have "path" and "content" fields
- Do NOT omit required fields

Action:"""