# ADR-002: AI Provider Selection

## Status
Accepted

## Context
The platform must generate AI-powered drafts and translations. The challenge requires integration with at least one of OpenAI or Anthropic SDKs. We need to decide which provider(s) to support and how to abstract them to allow switching or fallback without changing application logic.

The implementation consists of:
- A protocol/abstract base class `AIProvider` with methods `generate_draft(brief)` and `generate_translation(text, target_language)`
- Concrete providers: `OpenAIProvider` (gpt-4o) and `AnthropicProvider` (claude-sonnet-4-20250514)
- A factory function `get_provider()` at `apps/ai/providers/__init__.py` that reads `settings.AI_PROVIDER` to select the active provider
- `AiService` with automatic fallback: if the primary provider hits a rate limit or throws an unexpected error, it attempts the secondary provider before raising

## Decision
Support both OpenAI and Anthropic with a provider abstraction layer. Configure the active provider via the `AI_PROVIDER` environment variable, with automatic fallback to the other provider on failure.

### Key Design Details
| Concern | Decision | Rationale |
|---|---|---|
| Abstraction mechanism | Abstract base class (`AIProvider` protocol) | Allows compile-time type checking; both providers implement the same interface |
| Provider selection | Factory function in `apps/ai/providers/__init__.py` | Centralizes construction; reads `AI_PROVIDER` setting |
| Model selection | Configurable via `OPENAI_MODEL` / `ANTHROPIC_MODEL` settings | Defaults: gpt-4o, claude-sonnet-4-20250514 |
| Fallback | Automatic in `AiService._get_fallback_provider()` | Switches to the other provider on RateLimitError or unexpected failures |
| API key validation | Factory raises `ConfigurationError` if key is missing | Prevents runtime errors with informative message |
| Prompt management | Centralized in `apps/ai/prompts.py` | Both providers use the same prompt templates |

## Consequences
### Positive
- Supports both OpenAI and Anthropic SDKs (exceeds the minimum requirement of "at least one")
- Automatic fallback provides resilience — if one provider is rate-limited or down, the other is used transparently
- Provider abstraction allows future providers (e.g., Gemini, Llama) to be added by implementing `AIProvider` without changing the application logic
- Configuration via environment variables follows R-007 (no hardcoded secrets)
- Both providers return structured JSON (`headline`, `description`) so the parsing logic is shared

### Negative
- Maintaining two provider integrations increases test surface (both need mock-based unit tests per R-009)
- Each provider SDK introduces its own dependency and potential API drift
- Fallback logic adds complexity to `AiService` (must handle partial failures gracefully)
- Rate limit detection relies on string matching in error messages, which may be brittle across SDK versions

## Alternatives Considered
- **OpenAI only**: Rejected — single point of failure; no fallback if OpenAI is rate-limited or experiencing an outage. Also does not demonstrate multi-provider abstraction.
- **Anthropic only**: Rejected — same single-point-of-failure concern. Also, OpenAI's SDK has broader community adoption and more example patterns.
- **Both with abstraction layer (chosen)**: Provides resilience, flexibility, and demonstrates architectural best practices. The abstraction layer adds minimal complexity (one base class, two implementations, one factory) while enabling future provider additions.

## References
- AGENTS.md R-005: Must integrate at least one of OpenAI SDK or Anthropic SDK
- AGENTS.md R-007: No hardcoded secrets
- Implementation: `backend/apps/ai/providers/base.py` (AIProvider protocol)
- Implementation: `backend/apps/ai/providers/openai_provider.py` (OpenAIProvider)
- Implementation: `backend/apps/ai/providers/anthropic_provider.py` (AnthropicProvider)
- Implementation: `backend/apps/ai/providers/__init__.py` (get_provider factory)
- Implementation: `backend/apps/ai/services.py` (AiService with fallback)
