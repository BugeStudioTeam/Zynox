"""Grok (xAI) provider"""

import requests
import json
from .base import AIProvider

class GrokProvider(AIProvider):
    """Grok/xAI API provider"""
    
    API_URL = "https://api.x.ai/v1/chat/completions"
    
    def call(self, prompt: str, model: str = None) -> str:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        payload = {
            "model": model or "grok-beta",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.1,
            "max_tokens": 8192
        }
        
        response = requests.post(self.API_URL, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        
        result = response.json()
        return self.clean_response(result["choices"][0]["message"]["content"])