"""Gemini provider"""

import requests
import json
from .base import AIProvider

class GeminiProvider(AIProvider):
    """Google Gemini API provider"""
    
    API_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    
    def call(self, prompt: str, model: str = None) -> str:
        model = model or "gemini-1.5-flash"
        url = self.API_URL.replace("{model}", model)
        
        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": self.api_key
        }
        
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.1, "maxOutputTokens": 8192}
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        
        result = response.json()
        return self.clean_response(result["candidates"][0]["content"]["parts"][0]["text"])