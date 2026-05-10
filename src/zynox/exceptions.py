"""Custom exceptions for ZynoxAI"""

class ZynoxAIError(Exception):
    """Base exception for ZynoxAI"""
    pass

class APIKeyError(ZynoxAIError):
    """Raised when API key is missing or invalid"""
    pass

class CommandError(ZynoxAIError):
    """Raised when command execution fails"""
    pass

class FileNotFoundError(ZynoxAIError):
    """Raised when a file is not found"""
    pass

class PackageNotInstalledError(ZynoxAIError):
    """Raised when a required package is not installed"""
    pass