import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { wsService } from './websocket';
import type { WSSubscriber } from '../types/websocket';

class MockWebSocket {
  url: string;
  onopen: (() => void) | null = null;
  onclose: ((event: { code: number }) => void) | null = null;
  onmessage: ((event: MessageEvent) => void) | null = null;
  onerror: (() => void) | null = null;
  readyState: number = 0;

  constructor(url: string) {
    this.url = url;
  }

  close() {
    this.readyState = 3;
    this.onclose?.({ code: 1000 });
  }

  // Helper for tests to simulate open
  _open() {
    this.readyState = 1;
    this.onopen?.();
  }

  // Helper for tests to simulate message
  _send(data: string) {
    this.onmessage?.(new MessageEvent('message', { data }));
  }

  // Helper for tests to simulate close/error
  _close(code = 1006) {
    this.readyState = 3;
    this.onclose?.({ code });
  }
}

let mockWsInstances: MockWebSocket[] = [];

beforeEach(() => {
  mockWsInstances = [];
  vi.useFakeTimers();

  // @ts-expect-error - mocking WebSocket
  globalThis.WebSocket = vi.fn((url: string) => {
    const instance = new MockWebSocket(url);
    mockWsInstances.push(instance);
    return instance;
  });
});

afterEach(() => {
  vi.useRealTimers();
  wsService.disconnectAll();
  vi.restoreAllMocks();
});

function getLastWs(): MockWebSocket {
  return mockWsInstances[mockWsInstances.length - 1];
}

describe('WebSocketService', () => {
  it('connects to the correct URL', () => {
    const sub: WSSubscriber = {
      onEvent: vi.fn(),
      onStatusChange: vi.fn(),
    };

    wsService.subscribe('content-123', sub);
    const ws = getLastWs();
    expect(ws.url).toContain('/ws/content/content-123/');
  });

  it('triggers onEvent when message received', () => {
    const onEvent = vi.fn();
    const sub: WSSubscriber = { onEvent, onStatusChange: vi.fn() };

    wsService.subscribe('content-123', sub);
    const ws = getLastWs();
    ws._open();

    const payload = JSON.stringify({
      type: 'state.change',
      contentId: 'content-123',
      campaignId: 'camp-1',
      oldState: 'DRAFT',
      newState: 'SUGGESTED_BY_AI',
      action: 'GENERATE_AI',
      timestamp: '2025-01-01T00:00:00Z',
    });
    ws._send(payload);

    expect(onEvent).toHaveBeenCalledWith({
      type: 'state.change',
      contentId: 'content-123',
      campaignId: 'camp-1',
      oldState: 'DRAFT',
      newState: 'SUGGESTED_BY_AI',
      action: 'GENERATE_AI',
      timestamp: '2025-01-01T00:00:00Z',
    });
  });

  it('triggers onStatusChange when connecting and connected', () => {
    const onStatusChange = vi.fn();
    const sub: WSSubscriber = { onEvent: vi.fn(), onStatusChange };

    wsService.subscribe('content-123', sub);
    expect(onStatusChange).toHaveBeenCalledWith('connecting');

    const ws = getLastWs();
    ws._open();
    expect(onStatusChange).toHaveBeenCalledWith('connected');
  });

  it('reconnects on unexpected close', () => {
    const onStatusChange = vi.fn();
    const sub: WSSubscriber = { onEvent: vi.fn(), onStatusChange };

    wsService.subscribe('content-123', sub);
    const ws = getLastWs();
    ws._open();
    ws._close(1006);

    expect(onStatusChange).toHaveBeenCalledWith('reconnecting');

    vi.advanceTimersByTime(1000);
    expect(mockWsInstances.length).toBeGreaterThanOrEqual(2);
  });

  it('stops reconnecting when no subscribers left', () => {
    const sub: WSSubscriber = { onEvent: vi.fn(), onStatusChange: vi.fn() };

    const unsub = wsService.subscribe('content-123', sub);
    unsub();

    vi.advanceTimersByTime(5000);

    expect(mockWsInstances.length).toBe(1);
  });

  it('handles connection.ack event', () => {
    const onEvent = vi.fn();
    const sub: WSSubscriber = { onEvent, onStatusChange: vi.fn() };

    wsService.subscribe('content-456', sub);
    const ws = getLastWs();
    ws._open();

    ws._send(JSON.stringify({ type: 'connection.ack', contentId: 'content-456' }));
    expect(onEvent).toHaveBeenCalledWith({
      type: 'connection.ack',
      contentId: 'content-456',
    });
  });

  it('does not crash on malformed messages', () => {
    const onEvent = vi.fn();
    const sub: WSSubscriber = { onEvent, onStatusChange: vi.fn() };

    wsService.subscribe('content-123', sub);
    const ws = getLastWs();
    ws._open();

    expect(() => {
      ws._send('not valid json');
    }).not.toThrow();

    expect(onEvent).not.toHaveBeenCalled();
  });

  it('returns correct status via getStatus', () => {
    expect(wsService.getStatus('nonexistent')).toBe('disconnected');

    const sub: WSSubscriber = { onEvent: vi.fn(), onStatusChange: vi.fn() };
    wsService.subscribe('content-123', sub);
    expect(wsService.getStatus('content-123')).toBe('connecting');
  });

  it('uses multiple subscribers for same contentId', () => {
    const onEvent1 = vi.fn();
    const onEvent2 = vi.fn();
    const sub1: WSSubscriber = { onEvent: onEvent1, onStatusChange: vi.fn() };
    const sub2: WSSubscriber = { onEvent: onEvent2, onStatusChange: vi.fn() };

    wsService.subscribe('content-123', sub1);
    wsService.subscribe('content-123', sub2);
    const ws = getLastWs();
    ws._open();

    ws._send(JSON.stringify({ type: 'connection.ack', contentId: 'content-123' }));

    expect(onEvent1).toHaveBeenCalled();
    expect(onEvent2).toHaveBeenCalled();
  });

  it('unsubscribe stops receiving events', () => {
    const onEvent = vi.fn();
    const sub: WSSubscriber = { onEvent, onStatusChange: vi.fn() };

    const unsub = wsService.subscribe('content-123', sub);
    const ws = getLastWs();
    ws._open();
    unsub();

    ws._send(JSON.stringify({ type: 'connection.ack', contentId: 'content-123' }));
    expect(onEvent).not.toHaveBeenCalled();
  });

  it('uses exponential backoff for reconnection', () => {
    const sub: WSSubscriber = { onEvent: vi.fn(), onStatusChange: vi.fn() };
    wsService.subscribe('content-123', sub);

    const ws = getLastWs();
    ws._open();

    // Close and reconnect multiple times
    for (let i = 0; i < 5; i++) {
      const lastWs = mockWsInstances[mockWsInstances.length - 1];
      lastWs._close(1006);
      vi.advanceTimersByTime(1000 * Math.pow(2, i));
    }

    expect(mockWsInstances.length).toBeGreaterThan(3);
  });

  it('stops reconnecting after MAX_RECONNECT_ATTEMPTS', () => {
    const onStatusChange = vi.fn();
    const sub: WSSubscriber = { onEvent: vi.fn(), onStatusChange };

    wsService.subscribe('content-123', sub);
    const ws = getLastWs();
    ws._open();

    // Simulate 20 failed reconnect attempts
    for (let i = 0; i < 20; i++) {
      const lastWs = mockWsInstances[mockWsInstances.length - 1];
      lastWs._close(1006);
      vi.advanceTimersByTime(30_000);
    }

    // At this point the 20th timer has fired and connected, bumping
    // reconnectAttempts to 20. Close once more — scheduleReconnect
    // should see attempts >= 20, go to 'disconnected', and NOT create
    // a new WebSocket.
    const instanceCountBefore = mockWsInstances.length;
    mockWsInstances[mockWsInstances.length - 1]._close(1006);
    vi.advanceTimersByTime(60_000);
    expect(mockWsInstances.length).toBe(instanceCountBefore);
    expect(onStatusChange).toHaveBeenLastCalledWith('disconnected');
  });
});
