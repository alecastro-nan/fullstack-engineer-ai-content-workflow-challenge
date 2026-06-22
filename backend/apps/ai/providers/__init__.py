from django.conf import settings

from apps.ai.exceptions import ConfigurationError
from apps.ai.providers.base import AIProvider


def get_provider() -> AIProvider:
    provider_name = getattr(settings, "AI_PROVIDER", "openai")
    if provider_name == "openai":
        api_key = getattr(settings, "OPENAI_API_KEY", "")
        if not api_key:
            raise ConfigurationError("OPENAI_API_KEY not configured")
        from apps.ai.providers.openai_provider import OpenAIProvider
        return OpenAIProvider(
            api_key=api_key,
            model=getattr(settings, "OPENAI_MODEL", "gpt-4o"),
            temperature=getattr(settings, "AI_TEMPERATURE", 0.7),
            max_tokens=getattr(settings, "AI_MAX_TOKENS", 2048),
        )
    if provider_name == "anthropic":
        api_key = getattr(settings, "ANTHROPIC_API_KEY", "")
        if not api_key:
            raise ConfigurationError("ANTHROPIC_API_KEY not configured")
        from apps.ai.providers.anthropic_provider import AnthropicProvider
        return AnthropicProvider(
            api_key=api_key,
            model=getattr(settings, "ANTHROPIC_MODEL", "claude-sonnet-4-20250514"),
            temperature=getattr(settings, "AI_TEMPERATURE", 0.7),
            max_tokens=getattr(settings, "AI_MAX_TOKENS", 2048),
        )
    raise ConfigurationError(f"Unknown AI provider: {provider_name}")
