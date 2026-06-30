# Learning: 2026-06-26 - `sk-` prefix false-positive risk in test dummy keys

## Error
Secret scanners (gitLeaks, truffleHog) flagged `sk-test-*` and `sk-ant-test-*` dummy API keys in test files and CI config as potential secrets.

## Root Cause
The `sk-` prefix matches the real API key format for both OpenAI (`sk-...`) and Anthropic (`sk-ant-...`). Even though these keys were never used to call real APIs (mocked in unit tests, dummy in CI), secret scanners cannot distinguish them from real keys without semantic analysis.

## Solution
Renamed all 14 occurrences across 6 files from `sk-*` prefix to `test-invalid-*` prefix:
- `sk-test-key` → `test-invalid-key`
- `sk-ant-test-key` → `test-invalid-ant-key`
- `sk-test-fake-key` → `test-invalid-fake-key`
- `sk-test-e2e-key` → `test-invalid-e2e-key`

Each assignment annotated with `# Test-only dummy key — not a real credential`.

## Prevention
Always use `test-invalid-` prefix (never `sk-`) for dummy API keys in test files and CI configuration. This applies to both OpenAI and Anthropic keys.
