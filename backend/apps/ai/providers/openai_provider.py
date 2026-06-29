import json

from openai import OpenAI

from apps.ai.exceptions import MalformedResponseError, RateLimitError
from apps.ai.prompts import format_draft_prompt, format_translation_prompt
from apps.ai.providers.base import AIProvider, DraftResult, TranslationResult


class OpenAIProvider(AIProvider):
    def __init__(
        self,
        api_key: str,
        base_url: str | None = None,
        model: str = "gpt-4o",
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> None:
        if base_url:
            self.client = OpenAI(api_key=api_key, base_url=base_url)
        else:
            self.client = OpenAI(api_key=api_key)
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
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                timeout=30,
            )
        except Exception as exc:
            error_msg = str(exc).lower()
            if "rate" in error_msg or "429" in error_msg:
                raise RateLimitError(
                    f"OpenAI rate limit exceeded: {exc}"
                ) from exc
            raise

        choice = resp.choices[0]
        content = choice.message.content
        if content is None:
            raise MalformedResponseError("OpenAI returned empty response")
        return content

    @staticmethod
    def _parse_draft_response(content: str) -> DraftResult:
        try:
            data = json.loads(content)
        except json.JSONDecodeError as exc:
            raise MalformedResponseError(
                f"Failed to parse OpenAI draft response: {exc}"
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
                f"Failed to parse OpenAI translation response: {exc}"
            ) from exc
        return TranslationResult(
            headline=data.get("headline", ""),
            description=data.get("description", ""),
        )
