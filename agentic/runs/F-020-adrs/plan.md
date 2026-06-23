# Plan — F-020: Complete pending ADRs

## Status
✅ Done

## What needed to be done
1. Verify ADR-001, ADR-004, ADR-005, ADR-006 are still current with the actual implementation
2. Complete ADR-002 (AI Provider Selection) with final decision
3. Complete ADR-003 (Real-Time Mechanism) with final decision
4. Update feature_list.json and session-progress.md

## Verification results

### ADR-001 (REST vs GraphQL)
- Status: **Accepted** (superseded by ADR-005)
- Matches current implementation: ✅ (Strawberry GraphQL sole API layer)

### ADR-004 (Database Schema)
- Status: **Accepted**
- Matches current models: ✅ (campaigns, content_pieces tables, soft delete, UUID PKs)

### ADR-005 (Django + Strawberry Architecture)
- Status: **Accepted**
- Matches current stack: ✅ (Django 5.x, Strawberry GraphQL, Django ORM, pytest, uv)

### ADR-006 (Agentic Directory Structure)
- Status: **Accepted**
- Matches current structure: ✅ (all artifacts under /agentic/, symlinks at root)

## ADR-002 completion details
- Decision: Both OpenAI + Anthropic with abstraction layer
- Provider protocol: `AIProvider` base class (protocol) in `apps/ai/providers/base.py`
- Concrete providers: `OpenAIProvider` (gpt-4o), `AnthropicProvider` (claude-sonnet-4-20250514)
- Factory: `get_provider()` in `apps/ai/providers/__init__.py`
- Fallback: `AiService._get_fallback_provider()` auto-switches on rate limit or unexpected error

## ADR-003 completion details
- Decision: Django Channels WebSockets
- Routing: `ProtocolTypeRouter` in `config/asgi.py` routes `ws/content/{content_id}/`
- Consumer: `ContentConsumer` (AsyncWebsocketConsumer) in `apps/ws/consumers.py`
- Signal: `post_save` on `StateHistory` → `broadcast_state_change` in `apps/ws/signals.py`
- Group messaging: per-content-piece groups (`content_{id}`)

## Files modified
- `docs/adrs/ADR-002-ai-provider.md`: placeholders → full ADR with context, decision table, consequences, alternatives
- `docs/adrs/ADR-003-real-time-mechanism.md`: placeholders → full ADR with message format spec, decision table, consequences, alternatives
- `agentic/tasks/feature_list.json`: F-020 status → done
- `agentic/tasks/session-progress.md`: F-020 → DONE
- `agentic/runs/F-020-adrs/plan.md`: created
