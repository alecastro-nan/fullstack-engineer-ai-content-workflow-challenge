import { authService } from './auth';
import type { ConnectionStatus, WSInboundEvent, WSSubscriber } from '../types/websocket';

const RECONNECT_BASE_MS = 1000;
const RECONNECT_MAX_MS = 30_000;
const MAX_RECONNECT_ATTEMPTS = 20;

interface ConnectionState {
  ws: WebSocket | null;
  status: ConnectionStatus;
  subscribers: Set<WSSubscriber>;
  reconnectTimer: ReturnType<typeof setTimeout> | null;
  reconnectAttempts: number;
  intentionalClose: boolean;
}

class WebSocketService {
  private connections = new Map<string, ConnectionState>();

  private getBaseUrl(): string {
    return import.meta.env.VITE_WS_URL || 'ws://localhost:8000';
  }

  subscribe(
    contentId: string,
    subscriber: WSSubscriber,
  ): () => void {
    let state = this.connections.get(contentId);
    if (!state) {
      state = {
        ws: null,
        status: 'disconnected',
        subscribers: new Set(),
        reconnectTimer: null,
        reconnectAttempts: 0,
        intentionalClose: false,
      };
      this.connections.set(contentId, state);
    }

    state.subscribers.add(subscriber);

    if (state.status === 'disconnected') {
      this.connect(contentId);
    }

    return () => {
      const s = this.connections.get(contentId);
      if (!s) return;
      s.subscribers.delete(subscriber);
      if (s.subscribers.size === 0) {
        this.disconnect(contentId);
      }
    };
  }

  getStatus(contentId: string): ConnectionStatus {
    return this.connections.get(contentId)?.status ?? 'disconnected';
  }

  disconnectAll(): void {
    for (const contentId of this.connections.keys()) {
      this.disconnect(contentId);
    }
  }

  private connect(contentId: string): void {
    const state = this.connections.get(contentId);
    if (!state) return;

    state.intentionalClose = false;
    this.setStatus(contentId, 'connecting');

    const url = `${this.getBaseUrl()}/ws/content/${contentId}/`;
    const token = authService.getAccessToken();
    let ws: WebSocket;

    try {
      ws = new WebSocket(url, token ? [token] : undefined);
    } catch {
      this.scheduleReconnect(contentId);
      return;
    }

    state.ws = ws;

    ws.onopen = () => {
      const s = this.connections.get(contentId);
      if (!s) return;
      s.reconnectAttempts = 0;
      this.setStatus(contentId, 'connected');
    };

    ws.onmessage = (event: MessageEvent) => {
      const s = this.connections.get(contentId);
      if (!s) return;

      try {
        const data = JSON.parse(event.data) as WSInboundEvent;
        for (const sub of s.subscribers) {
          sub.onEvent(data);
        }
      } catch (e) {
        console.warn('Malformed WebSocket message:', e);
      }
    };

    ws.onclose = () => {
      const s = this.connections.get(contentId);
      if (!s) return;
      s.ws = null;
      if (!s.intentionalClose) {
        this.setStatus(contentId, 'reconnecting');
        this.scheduleReconnect(contentId);
      } else {
        this.setStatus(contentId, 'disconnected');
        if (s.subscribers.size === 0) {
          this.connections.delete(contentId);
        }
      }
    };

    ws.onerror = () => {
      // onclose will fire after onerror, triggering reconnection
    };
  }

  private disconnect(contentId: string): void {
    const state = this.connections.get(contentId);
    if (!state) return;

    state.intentionalClose = true;

    if (state.reconnectTimer) {
      clearTimeout(state.reconnectTimer);
      state.reconnectTimer = null;
    }

    if (state.ws) {
      state.ws.close();
      state.ws = null;
    }

    this.setStatus(contentId, 'disconnected');
    this.connections.delete(contentId);
  }

  private scheduleReconnect(contentId: string): void {
    const state = this.connections.get(contentId);
    if (!state) return;

    if (state.reconnectTimer) return;

    if (state.reconnectAttempts >= MAX_RECONNECT_ATTEMPTS) {
      this.setStatus(contentId, 'disconnected');
      this.connections.delete(contentId);
      return;
    }

    const delay = Math.min(
      RECONNECT_BASE_MS * Math.pow(2, state.reconnectAttempts),
      RECONNECT_MAX_MS,
    );
    state.reconnectAttempts += 1;

    state.reconnectTimer = setTimeout(() => {
      const s = this.connections.get(contentId);
      if (!s) return;
      s.reconnectTimer = null;
      this.connect(contentId);
    }, delay);
  }

  private setStatus(contentId: string, status: ConnectionStatus): void {
    const state = this.connections.get(contentId);
    if (!state) return;
    state.status = status;
    for (const sub of state.subscribers) {
      sub.onStatusChange(status);
    }
  }
}

export const wsService = new WebSocketService();
