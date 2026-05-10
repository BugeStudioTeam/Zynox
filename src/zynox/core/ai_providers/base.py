"""Base class for AI providers"""

from abc import ABC, abstractmethod
import re

class AIProvider(ABC):
    """Abstract base class for AI providers"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.model = None
    
    @abstractmethod
    def call(self, prompt: str, model: str = None) -> str:
        """Call the AI API and return response"""
        pass
    
    def clean_response(self, response: str) -> str:
        """Clean AI response by removing markdown code blocks"""
        response = re.sub(r'```json\s*', '', response)
        response = re.sub(r'```\s*', '', response)
        return response.strip()