# Skill: AI Integration

## Purpose
Learn how to abstract OpenAI and Anthropic API calls, manage prompt templates, and implement retry/fallback logic.

## When to Use
- When implementing the AI provider abstraction (F-004)
- When adding new AI capabilities (draft generation, translation)
- When modifying prompt templates

## Steps

### 1. Provider Interface
```
AiProvider
├── generateDraft(brief: string): DraftResult
├── translate(text: string, targetLang: string): TranslationResult
└── extractStructuredData(text: string): DataExtractionResult
```

### 2. OpenAI Provider
- Use `openai` npm package (v4+)
- Initialize with `new OpenAI({ apiKey: process.env.OPENAI_API_KEY })`
- Use `chat.completions.create()` with gpt-4 or gpt-3.5-turbo
- Implement retry with exponential backoff (3 attempts max)

### 3. Anthropic Provider
- Use `@anthropic-ai/sdk` npm package
- Initialize with `new Anthropic({ apiKey: process.env.ANTHROPIC_API_KEY })`
- Use `messages.create()` with claude-3-haiku or claude-3-sonnet
- Implement retry with exponential backoff (3 attempts max)

### 4. Prompt Management
- Store prompts as template functions, not inline strings
- Example: `const DRAFT_PROMPT = (brief: string) => \`Generate content...\`;`
- Prompts live in `src/ai/prompts/`
- Use temperature=0.7 for creative tasks, temperature=0.2 for extraction

### 5. Fallback Logic
- Try primary provider → on failure → try secondary provider
- If both fail, throw `AiProviderError` with details
- Log each attempt with duration and provider name

### 6. Mocking for Tests
- Use jest.mock or vitest.mock with a factory returning mock data
- Test: success path, provider failure, all providers failure
- Never make real API calls in unit tests

## Verification
- Unit tests pass with mocked providers
- Integration test confirms fallback works
- No API keys in source code or logs
