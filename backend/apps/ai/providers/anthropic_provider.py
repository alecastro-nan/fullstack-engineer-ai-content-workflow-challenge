import json

from anthropic import Anthropic

from apps.ai.exceptions import MalformedResponseError, RateLimitError
from apps.ai.prompts import DRAFT_PROMPT, TRANSLATION_PROMPT
from apps.ai.providers.base import AIProvider, DraftResult, TranslationResult


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
        prompt = DRAFT_PROMPT.format(brief=brief)
        response = self._call_api(prompt)
        return self._parse_draft_response(response)

    def translate(self, text: str, target_language: str) -> TranslationResult:
        prompt = TRANSLATION_PROMPT.format(
            headline=text,
            description=text,
            target_language=target_language,
        )
        response = self._call_api(prompt)
        return self._parse_translation_response(response)

    def _call_api(self, prompt: str) -> str:
        try:
            resp = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                messages=[{"role": "user", "content": prompt}],
            )
        except Exception as exc:
            error_msg = str(exc).lower()
            if "rate" in error_msg or "429" in error_msg:
                raise RateLimitError(
                    f"Anthropic rate limit exceeded: {exc}"
                ) from exc
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
