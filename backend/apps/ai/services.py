import logging

from django.conf import settings

from apps.ai.exceptions import AIProviderError, ConfigurationError, RateLimitError
from apps.ai.providers import get_provider
from apps.ai.providers.base import AIProvider, DraftResult, TranslationResult

logger = logging.getLogger(__name__)


class AiService:
    @staticmethod
    def generate_draft(brief: str) -> DraftResult:
        provider = get_provider()
        try:
            return provider.generate_draft(brief)
        except RateLimitError:
            logger.warning("Rate limited on primary provider, attempting fallback")
            fallback = AiService._get_fallback_provider()
            if fallback is not None:
                return fallback.generate_draft(brief)
            raise
        except AIProviderError:
            raise
        except Exception as exc:
            logger.error("Primary AI provider failed: %s", exc)
            fallback = AiService._get_fallback_provider()
            if fallback is None:
                raise
            logger.info("Falling back to secondary AI provider")
            return fallback.generate_draft(brief)

    @staticmethod
    def translate(text: str, target_language: str) -> TranslationResult:
        provider = get_provider()
        try:
            return provider.translate(text, target_language)
        except RateLimitError:
            logger.warning("Rate limited on primary provider, attempting fallback")
            fallback = AiService._get_fallback_provider()
            if fallback is not None:
                return fallback.translate(text, target_language)
            raise
        except AIProviderError:
            raise
        except Exception as exc:
            logger.error("Primary AI provider failed: %s", exc)
            fallback = AiService._get_fallback_provider()
            if fallback is None:
                raise
            logger.info("Falling back to secondary AI provider")
            return fallback.translate(text, target_language)

    @staticmethod
    def _get_fallback_provider() -> AIProvider | None:
        primary = getattr(settings, "AI_PROVIDER", "openai")
        fallback_name = "anthropic" if primary == "openai" else "openai"
        try:
            return get_provider(provider_name=fallback_name)
        except ConfigurationError:
            return None
