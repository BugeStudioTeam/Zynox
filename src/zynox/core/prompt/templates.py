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
Complete when task is done."""

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
Output ONLY ONE JSON action. Do NOT output multiple actions.
When the task is completely done, output COMPLETE.

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
Remember to check if files exist before reading them.

Action:"""