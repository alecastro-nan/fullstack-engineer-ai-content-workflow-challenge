import json
from unittest.mock import MagicMock, patch

import pytest
import httpx
from anthropic import APIError

from apps.ai.exceptions import MalformedResponseError, RateLimitError
from apps.ai.providers.anthropic_provider import AnthropicProvider


@pytest.fixture
def provider() -> AnthropicProvider:
    return AnthropicProvider(
        api_key="test-invalid-ant-key",
    )


class TestAnthropicProviderGenerateDraft:
    def test_success(self, provider: AnthropicProvider) -> None:
        with patch.object(provider.client.messages, "create") as mock_create:
            mock_block = MagicMock()
            mock_block.text = json.dumps(
                {"headline": "AI Headline", "description": "AI Description"}
            )
            mock_create.return_value = MagicMock(content=[mock_block])

            result = provider.generate_draft("Test brief")

            assert result.headline == "AI Headline"
            assert result.description == "AI Description"

    def test_malformed_response_json_error(self, provider: AnthropicProvider) -> None:
        with patch.object(provider, "_call_api", return_value="not-json"), \
             pytest.raises(MalformedResponseError):
            provider.generate_draft("Test brief")

    def test_empty_response(self, provider: AnthropicProvider) -> None:
        mock_resp = MagicMock()
        mock_resp.content = []
        with patch.object(provider.client.messages, "create", return_value=mock_resp), \
             pytest.raises(MalformedResponseError, match="empty"):
            provider._call_api("prompt")

    def test_rate_limit_error(self, provider: AnthropicProvider) -> None:
        with patch.object(
            provider.client.messages,
            "create",
            side_effect=APIError("rate limit exceeded 429", httpx.Request("POST", "https://api.anthropic.com"), body=None),
        ), pytest.raises(RateLimitError):
            provider._call_api("prompt")

    def test_generic_api_error(self, provider: AnthropicProvider) -> None:
        with patch.object(
            provider.client.messages,
            "create",
            side_effect=Exception("Connection refused"),
        ), pytest.raises(Exception, match="Connection refused"):
            provider._call_api("prompt")


class TestAnthropicProviderTranslate:
    def test_success(self, provider: AnthropicProvider) -> None:
        with patch.object(provider.client.messages, "create") as mock_create:
            mock_block = MagicMock()
            mock_block.text = json.dumps(
                {"headline": "Título", "description": "Descripción"}
            )
            mock_create.return_value = MagicMock(content=[mock_block])

            result = provider.translate(
                "Headline: English Title\nDescription: English Desc", "es"
            )

            assert result.headline == "Título"
            assert result.description == "Descripción"

    def test_translate_parsing_both_present(self) -> None:
        p = AnthropicProvider(api_key="test-invalid-ant-key")
        text = "Headline: Cool Product\nDescription: Best product ever"
        with patch.object(p, "_call_api") as mock_call:
            mock_call.return_value = json.dumps(
                {"headline": "Producto Genial", "description": "El mejor producto"}
            )
            result = p.translate(text, "es")
            assert result.headline == "Producto Genial"
            assert result.description == "El mejor producto"

    def test_translate_parsing_missing_headline(self) -> None:
        p = AnthropicProvider(api_key="test-invalid-ant-key")
        text = "Description: Only description provided"
        with patch.object(p, "_call_api") as mock_call:
            mock_call.return_value = json.dumps(
                {"headline": "", "description": "Solo descripción"}
            )
            result = p.translate(text, "fr")
            assert result.headline == ""
            assert result.description == "Solo descripción"

    def test_translate_parsing_missing_description(self) -> None:
        p = AnthropicProvider(api_key="test-invalid-ant-key")
        text = "Headline: Title only"
        with patch.object(p, "_call_api") as mock_call:
            mock_call.return_value = json.dumps(
                {"headline": "Solo título", "description": ""}
            )
            result = p.translate(text, "de")
            assert result.headline == "Solo título"
            assert result.description == ""

    def test_translate_malformed_json(self, provider: AnthropicProvider) -> None:
        with patch.object(provider, "_call_api", return_value="not-json"), \
             pytest.raises(MalformedResponseError):
            provider.translate("Headline: Test\nDescription: Test", "es")
