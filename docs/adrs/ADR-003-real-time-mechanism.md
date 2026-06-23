# ADR-003: Real-Time Mechanism

## Status
Accepted

## Context
The platform must show updates to all users in real-time when content state changes (AI draft generated, review action taken, translation completed). Multiple users may be viewing the same campaign detail page and should see state transitions (DRAFT → SUGGESTED_BY_AI → REVIEWED → APPROVED/REJECTED) without manual page refresh.

The challenge requirement states: "Real-time features with WebSockets, GraphQL Subscriptions, or SSE" — any of the three is acceptable.

The implementation consists of:
- Django Channels with a `ProtocolTypeRouter` in `config/asgi.py` that routes WebSocket connections
- A `ContentConsumer` (AsyncWebsocketConsumer) at `apps/ws/consumers.py` that manages per-content-piece group subscriptions
- A `post_save` signal handler on `StateHistory` at `apps/ws/signals.py` that broadcasts state changes to the content piece's group
- WebSocket URL pattern: `ws/content/{content_id}/`

## Decision
Use Django Channels with WebSockets for real-time communication.

### Key Design Details
| Concern | Decision | Rationale |
|---|---|---|
| Protocol | WebSockets via Django Channels | Bidirectional communication; built-in Django integration via ASGI |
| Routing | `ProtocolTypeRouter` in asgi.py | Separates HTTP and WebSocket traffic at the protocol level |
| Consumer | AsyncWebsocketConsumer | Non-blocking; handles many concurrent connections efficiently |
| Group messaging | Per-content-piece groups (`content_{id}`) | Each content piece has its own group; clients subscribe only to relevant updates |
| Broadcast trigger | Django `post_save` signal on `StateHistory` | Decouples state tracking from broadcast logic; fires automatically on any state change |
| Discovery | No central room registry | Group join/leave is managed by the consumer on connect/disconnect |

### WebSocket Message Format
```json
{
  "type": "state.change",
  "payload": {
    "contentId": "uuid",
    "campaignId": "uuid",
    "oldState": "suggested_by_ai",
    "newState": "approved",
    "action": "approve",
    "timestamp": "2025-01-01T12:00:00+00:00"
  }
}
```

## Consequences
### Positive
- Django Channels is a first-party Django extension with mature ASGI support
- WebSockets provide full-duplex communication (useful for future features like collaborative editing)
- Per-content-piece groups minimize unnecessary message traffic (clients only receive updates for pieces they're viewing)
- Signal-based broadcast is decoupled from the business logic — state changes are broadcast automatically without modifying mutation resolvers
- ASGI configuration allows HTTP and WebSocket to coexist on the same port

### Negative
- WebSockets require an ASGI server (uvicorn/daphne) rather than the simpler WSGI (gunicorn)
- Django Channels requires Redis for production channel layer (in-memory layer is sufficient for single-process dev but doesn't scale horizontally)
- WebSocket connections consume server resources even when idle (mitigation: connection timeout on consumer)
- Signal-based broadcast fires on every StateHistory creation, even if no clients are subscribed (mitigation: lightweight — just a group_send that goes nowhere if group is empty)
- Frontend needs a WebSocket client library with reconnection logic (implemented in `frontend/src/services/websocket.ts`)

## Alternatives Considered
- **Server-Sent Events (SSE)**: Rejected — unidirectional (server→client only); would prevent future features like client-initiated refresh requests. Also lacks native Django integration (no Channels equivalent) and requires manual connection management.
- **GraphQL Subscriptions**: Rejected — Strawberry GraphQL supports subscriptions, but they require the same WebSocket infrastructure as Django Channels. Adding GraphQL subscriptions on top of Channels would duplicate the transport layer (subscriptions need a WebSocket endpoint, which Channels already provides). The team would also need to learn subscription resolver patterns.
- **Polling (long-polling)**: Rejected — introduces latency (best case = poll interval), wastes server and network resources on repeated HTTP requests, and doesn't meet the "real-time" requirement for immediate state transition visibility.
- **Django Channels WebSockets (chosen)**: Full-duplex, mature Django integration, supports horizontal scaling via Redis channel layer, and allows future feature growth. The `ContentConsumer` pattern is well-documented and easy to test.

## References
- AGENTS.md requirement: "Real-time features with WebSockets, GraphQL Subscriptions, or SSE"
- Implementation: `backend/config/asgi.py` (ProtocolTypeRouter)
- Implementation: `backend/apps/ws/routing.py` (websocket_urlpatterns)
- Implementation: `backend/apps/ws/consumers.py` (ContentConsumer)
- Implementation: `backend/apps/ws/signals.py` (broadcast_state_change signal handler)
- Tests: `backend/apps/ws/tests/` (consumer + signal unit tests)
