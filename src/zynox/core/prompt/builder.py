"""Prompt builder for AI requests - Updated for step-by-step"""

import os
from .templates import load_rules, build_initial_prompt, build_step_prompt

class PromptBuilder:
    """Build prompts for AI requests"""
    
    @staticmethod
    def get_rules() -> str:
        """Get execution rules"""
        return load_rules()
    
    @staticmethod
    def create_initial_prompt(user_input: str, context: str = "", file_list: str = "") -> str:
        """Create initial prompt for first step"""
        env_info = f"\n[Environment: {os.environ.get('TERMUX_VERSION', 'Linux')}]\n"
        file_list_section = f"\nCurrent Directory Files:\n{file_list[:1000]}\n" if file_list else ""
        
        return build_initial_prompt(user_input, env_info + file_list_section + context)
    
    @staticmethod
    def create_step_prompt(user_input: str, step_result: str, context: str = "", step_number: int = 1) -> str:
        """Create prompt for subsequent steps"""
        return build_step_prompt(user_input, step_result, context, step_number)
    
    @staticmethod
    def create_prompt(user_input: str, context: str = "", file_list: str = "") -> str:
        """Legacy method for backward compatibility"""
        return PromptBuilder.create_initial_prompt(user_input, context, file_list)