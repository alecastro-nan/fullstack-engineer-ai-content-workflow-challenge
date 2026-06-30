import json
import logging

from anthropic import APIError, Anthropic

from apps.ai.exceptions import MalformedResponseError, RateLimitError
from apps.ai.prompts import format_draft_prompt, format_translation_prompt
from apps.ai.providers.base import AIProvider, DraftResult, TranslationResult

logger = logging.getLogger(__name__)


class AnthropicProvider(AIProvider):
    def __init__(
        self,
        api_key: str,
        model: str = "claude-sonnet-4-20250514",
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> None:
        self.client = Anthropic(api_key=api_key)
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

    def generate_draft(self, brief: str) -> DraftResult:
        prompt = format_draft_prompt(brief)
        response = self._call_api(prompt)
        return self._parse_draft_response(response)

    def translate(self, text: str, target_language: str) -> TranslationResult:
        # text format expected: "Headline: <headline>\nDescription: <description>"
        lines = text.split("\n", 1)
        headline = ""
        description = ""
        for line in lines:
            if line.startswith("Headline: "):
                headline = line.removeprefix("Headline: ")
            elif line.startswith("Description: "):
                description = line.removeprefix("Description: ")
        prompt = format_translation_prompt(headline, description, target_language)
        response = self._call_api(prompt)
        return self._parse_translation_response(response)

    def _call_api(self, prompt: str) -> str:
        try:
            resp = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                messages=[{"role": "user", "content": prompt}],
                timeout=60,
            )
        except APIError as exc:
            error_msg = str(exc).lower()
            if "rate" in error_msg or "429" in error_msg:
                raise RateLimitError(
                    f"Anthropic rate limit exceeded: {exc}"
                ) from exc
            logger.error("Anthropic API error: %s", exc)
            raise

        content = ""
        for block in resp.content:
            if hasattr(block, "text"):
                content = block.text
                break
        if not content:
            raise MalformedResponseError("Anthropic returned empty response")
        return content

    @staticmethod
    def _parse_draft_response(content: str) -> DraftResult:
        try:
            data = json.loads(content)
        except json.JSONDecodeError as exc:
            raise MalformedResponseError(
                f"Failed to parse Anthropic draft response: {exc}"
            ) from exc
        return DraftResult(
            headline=data.get("headline", ""),
            description=data.get("description", ""),
        )

    @staticmethod
    def _parse_translation_response(content: str) -> TranslationResult:
        try:
            data = json.loads(content)
        except json.JSONDecodeError as exc:
            raise MalformedResponseError(
                f"Failed to parse Anthropic translation response: {exc}"
            ) from exc
        return TranslationResult(
            headline=data.get("headline", ""),
            description=data.get("description", ""),
        )
