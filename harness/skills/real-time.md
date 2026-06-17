# Skill: Real-Time Communication

## Purpose
Learn how to set up WebSocket or SSE communication in the chosen backend framework for broadcasting state changes.

## When to Use
- When setting up real-time infrastructure (F-009)
- When broadcasting state changes (F-010)
- When connecting frontend to real-time events (F-017)

## Steps

### 1. Choose Mechanism
- **WebSockets (Socket.io)**: bidirectional, rooms, auto-reconnect. Best for this project.
- **SSE (Server-Sent Events)**: simpler, unidirectional (server→client). Good for state broadcasts only.
- **GraphQL Subscriptions**: requires GraphQL setup. Overkill if REST is chosen.

### 2. WebSocket Setup (NestJS with Socket.io)
- Install: `@nestjs/platform-socket.io`, `socket.io`, `socket.io-client`
- Create `RealtimeGateway` with `@WebSocketGateway({ cors: true })`
- Implement: `handleConnection`, `handleDisconnect`
- Emit events: `this.server.emit('content:state-changed', payload)`

### 3. WebSocket Setup (FastAPI)
- Install: `python-socketio` (async server)
- Create Socket.IO server: `sio = socketio.AsyncServer(async_mode='asgi')`
- Wrap with ASGI app
- Emit events: `await sio.emit('content:state-changed', payload)`

### 4. Event Payload Structure
```json
{
  "event": "content:state-changed",
  "data": {
    "contentId": "uuid",
    "campaignId": "uuid",
    "oldState": "draft",
    "newState": "suggested_by_ai",
    "timestamp": "2025-01-01T00:00:00Z",
    "payload": {}
  }
}
```

### 5. Integration Points
- After AI draft generation → emit event
- After review action → emit event
- After translation → emit event
- Frontend listens and updates UI accordingly

## Verification
- Client can connect and receive welcome event
- State change produces a WebSocket event
- Multiple clients receive broadcasts
- Frontend toast/notification appears on event
- Auto-reconnect works when server restarts
