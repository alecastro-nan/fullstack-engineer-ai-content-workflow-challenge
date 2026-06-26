import json
from unittest.mock import MagicMock, patch

import pytest
from django.test import TestCase, override_settings

from apps.ai.exceptions import (
    ConfigurationError,
    MalformedResponseError,
    RateLimitError,
)
from apps.ai.providers.base import DraftResult, TranslationResult
from apps.ai.services import AiService


class TestAiService(TestCase):
    def setUp(self) -> None:
        self.sample_brief = "Create content about AI technology"
        self.sample_draft = {
            "headline": "The Future of AI",
            "description": "AI is transforming industries worldwide.",
        }

    @override_settings(
        AI_PROVIDER="openai",
        OPENAI_API_KEY="test-invalid-key"  # Test-only dummy key — not a real credential,
        ANTHROPIC_API_KEY="",
    )
    @patch("apps.ai.providers.openai_provider.OpenAI")
    def test_generate_draft_with_openai(self, mock_openai: MagicMock) -> None:
        mock_instance = MagicMock()
        mock_instance.chat.completions.create.return_value = self._mock_openai_response(
            json.dumps(self.sample_draft)
        )
        mock_openai.return_value = mock_instance

        result = AiService.generate_draft(self.sample_brief)

        assert isinstance(result, DraftResult)
        assert result.headline == "The Future of AI"
        assert result.description == "AI is transforming industries worldwide."

    @override_settings(
        AI_PROVIDER="anthropic",
        ANTHROPIC_API_KEY="test-invalid-ant-key"  # Test-only dummy key — not a real credential,
        OPENAI_API_KEY="",
    )
    @patch("apps.ai.providers.anthropic_provider.Anthropic")
    def test_generate_draft_with_anthropic(self, mock_anthropic: MagicMock) -> None:
        mock_instance = MagicMock()
        mock_instance.messages.create.return_value = self._mock_anthropic_response(
            json.dumps(self.sample_draft)
        )
        mock_anthropic.return_value = mock_instance

        result = AiService.generate_draft(self.sample_brief)

        assert isinstance(result, DraftResult)
        assert result.headline == "The Future of AI"

    @override_settings(
        AI_PROVIDER="openai",
        OPENAI_API_KEY="test-invalid-key"  # Test-only dummy key — not a real credential,
        ANTHROPIC_API_KEY="test-invalid-ant-key"  # Test-only dummy key — not a real credential,
    )
    @patch("apps.ai.providers.openai_provider.OpenAI")
    @patch("apps.ai.providers.anthropic_provider.Anthropic")
    def test_fallback_on_openai_failure(
        self, mock_anthropic: MagicMock, mock_openai: MagicMock
    ) -> None:
        mock_openai_instance = MagicMock()
        mock_openai_instance.chat.completions.create.side_effect = Exception(
            "OpenAI API timeout"
        )
        mock_openai.return_value = mock_openai_instance

        mock_anthropic_instance = MagicMock()
        mock_anthropic_instance.messages.create.return_value = (
            self._mock_anthropic_response(json.dumps(self.sample_draft))
        )
        mock_anthropic.return_value = mock_anthropic_instance

        result = AiService.generate_draft(self.sample_brief)

        assert isinstance(result, DraftResult)
        assert result.headline == "The Future of AI"

    @override_settings(
        AI_PROVIDER="openai",
        OPENAI_API_KEY="",
        ANTHROPIC_API_KEY="",
    )
    def test_no_api_key_raises_error(self) -> None:
        with pytest.raises(ConfigurationError):
            AiService.generate_draft(self.sample_brief)

    @override_settings(
        AI_PROVIDER="openai",
        OPENAI_API_KEY="test-invalid-key"  # Test-only dummy key — not a real credential,
        ANTHROPIC_API_KEY="",
    )
    @patch("apps.ai.providers.openai_provider.OpenAI")
    def test_malformed_response_raises_error(self, mock_openai: MagicMock) -> None:
        mock_instance = MagicMock()
        mock_instance.chat.completions.create.return_value = self._mock_openai_response(
            "not-json-at-all"
        )
        mock_openai.return_value = mock_instance

        with pytest.raises(MalformedResponseError):
            AiService.generate_draft(self.sample_brief)

    @override_settings(
        AI_PROVIDER="openai",
        OPENAI_API_KEY="test-invalid-key"  # Test-only dummy key — not a real credential,
        ANTHROPIC_API_KEY="",
    )
    @patch("apps.ai.providers.openai_provider.OpenAI")
    def test_translate_with_openai(self, mock_openai: MagicMock) -> None:
        translation = {
            "headline": "El Futuro de la IA",
            "description": "La IA está transformando industrias en todo el mundo.",
        }
        mock_instance = MagicMock()
        mock_instance.chat.completions.create.return_value = self._mock_openai_response(
            json.dumps(translation)
        )
        mock_openai.return_value = mock_instance

        result = AiService.translate("The Future of AI", "es")

        assert isinstance(result, TranslationResult)
        assert result.headline == "El Futuro de la IA"

    @override_settings(
        AI_PROVIDER="openai",
        OPENAI_API_KEY="test-invalid-key"  # Test-only dummy key — not a real credential,
        ANTHROPIC_API_KEY="test-invalid-ant-key"  # Test-only dummy key — not a real credential,
    )
    @patch("apps.ai.providers.openai_provider.OpenAI")
    @patch("apps.ai.providers.anthropic_provider.Anthropic")
    def test_fallback_on_rate_limit(
        self, mock_anthropic: MagicMock, mock_openai: MagicMock
    ) -> None:
        mock_openai_instance = MagicMock()
        mock_openai_instance.chat.completions.create.side_effect = Exception(
            "Rate limit exceeded: 429"
        )
        mock_openai.return_value = mock_openai_instance

        mock_anthropic_instance = MagicMock()
        mock_anthropic_instance.messages.create.return_value = (
            self._mock_anthropic_response(json.dumps(self.sample_draft))
        )
        mock_anthropic.return_value = mock_anthropic_instance

        result = AiService.generate_draft(self.sample_brief)
        assert isinstance(result, DraftResult)

    @override_settings(
        AI_PROVIDER="openai",
        OPENAI_API_KEY="test-invalid-key"  # Test-only dummy key — not a real credential,
        ANTHROPIC_API_KEY="",
    )
    @patch("apps.ai.providers.openai_provider.OpenAI")
    def test_rate_limit_raises_exception(self, mock_openai: MagicMock) -> None:
        mock_instance = MagicMock()
        mock_instance.chat.completions.create.side_effect = Exception(
            "429 Too Many Requests"
        )
        mock_openai.return_value = mock_instance

        with pytest.raises(RateLimitError):
            AiService.generate_draft(self.sample_brief)

    @staticmethod
    def _mock_openai_response(content: str) -> MagicMock:
        mock_choice = MagicMock()
        mock_choice.message.content = content
        mock_resp = MagicMock()
        mock_resp.choices = [mock_choice]
        return mock_resp

    @staticmethod
    def _mock_anthropic_response(content: str) -> MagicMock:
        mock_content_block = MagicMock()
        mock_content_block.text = content
        mock_resp = MagicMock()
        mock_resp.content = [mock_content_block]
        return mock_resp
