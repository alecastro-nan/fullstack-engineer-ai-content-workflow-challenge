class AIProviderError(Exception):
    """Base exception for AI provider failures."""


class ConfigurationError(AIProviderError):
    """Raised when AI provider is not properly configured."""


class RateLimitError(AIProviderError):
    """Raised when API rate limit is exceeded."""


class MalformedResponseError(AIProviderError):
    """Raised when AI provider returns unexpected format."""
