# Handoff — F-009: AI Provider Abstraction Layer

## Meta
- **From:** Builder
- **To:** Code Reviewer
- **Date:** 2026-06-22

## What was done
- `providers/base.py` — `AIProvider` ABC with `generate_draft(brief)` and `translate(text, target_language)` methods, `DraftResult` and `TranslationResult` dataclasses
- `providers/openai_provider.py` — `OpenAIProvider` using `openai` SDK, rate limit detection, JSON response parsing
- `providers/anthropic_provider.py` — `AnthropicProvider` using `anthropic` SDK, rate limit detection, JSON response parsing
- `providers/__init__.py` — `get_provider()` registry with env-based selection (`AI_PROVIDER=openai|anthropic`), API key validation
- `prompts.py` — Externalized `DRAFT_PROMPT` and `TRANSLATION_PROMPT` with `{brief}`, `{target_language}`, `{headline}`, `{description}` placeholders, structured JSON output instructions
- `services.py` — `AiService` with auto-fallback: `RateLimitError` triggers secondary provider, other `AIProviderError` re-raised, unknown exceptions trigger fallback
- `exceptions.py` — `AIProviderError` (base), `ConfigurationError`, `RateLimitError`, `MalformedResponseError`
- `tests/test_ai_service.py` — 8 mock-based tests covering: OpenAI success, Anthropic success, fallback on failure, fallback on rate limit, rate limit error propagation, missing API key, malformed response, translation

## Design decisions
- `RateLimitError` triggers fallback to secondary provider (tiered fallback)
- `ConfigurationError` and `MalformedResponseError` re-raise immediately (fallback won't help)
- Unknown exceptions (timeout, network) trigger fallback to secondary
- Provider selection via `settings.AI_PROVIDER` env var (`"openai"` or `"anthropic"`)
- Both SDKs pinned in `pyproject.toml` (`openai>=1.55,<2`, `anthropic>=0.49,<1`)

## Quality gates
- **8/8 AI tests passing** ✅
- **106/106 full suite passing** ✅
- **mypy strict**: 0 errors ✅
- **ruff**: All checks passed ✅
- **All AI tests use mocks** — no real API calls (R-009)

## Not done / known issues
- AI schema mutations still stub (will be populated in F-010, F-011)
- `config/schema.py` not updated yet (no queries/mutations to register at abstraction layer)
- No documentation updated yet (README.md AI config section, docs/architecture.md diagram)

## Next actions
1. Code Reviewer: review AI provider pattern, verify mock tests, confirm no API key leaks
2. Security Reviewer: verify API key handling (env-only, no hardcoded keys)
3. Proceed to F-010 (AI draft mutation) or F-011 (AI translation mutation)
4. F-012 (Campaign Dashboard) can run in parallel

## Files created
- `backend/apps/ai/providers/__init__.py`
- `backend/apps/ai/providers/base.py`
- `backend/apps/ai/providers/openai_provider.py`
- `backend/apps/ai/providers/anthropic_provider.py`
- `backend/apps/ai/prompts.py`
- `backend/apps/ai/services.py`
- `backend/apps/ai/exceptions.py`
- `backend/apps/ai/tests/test_ai_service.py`
