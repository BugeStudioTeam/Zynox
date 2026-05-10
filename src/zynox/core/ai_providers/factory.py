"""Factory for creating AI providers"""

from .openai import OpenAIProvider
from .gemini import GeminiProvider
from .grok import GrokProvider
from .deepseek import DeepSeekProvider

class AIProviderFactory:
    """Factory class for creating AI provider instances"""
    
    _providers = {
        "openai": OpenAIProvider,
        "gemini": GeminiProvider,
        "grok": GrokProvider,
        "deepseek": DeepSeekProvider,
    }
    
    @classmethod
    def create(cls, provider_name: str, api_key: str):
        """Create an AI provider instance"""
        provider_name = provider_name.lower()
        if provider_name not in cls._providers:
            raise ValueError(f"Unknown provider: {provider_name}")
        return cls._providers[provider_name](api_key)
    
    @classmethod
    def get_available_providers(cls):
        """Get list of available providers"""
        return list(cls._providers.keys())