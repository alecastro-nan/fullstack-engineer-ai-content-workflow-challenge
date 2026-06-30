import { useEffect, useRef, useState } from 'react';
import { wsService } from '../services/websocket';
import type { ConnectionStatus, WSInboundEvent, WSSubscriber } from '../types/websocket';

export interface UseWebSocketResult {
  status: ConnectionStatus;
  lastEvent: WSInboundEvent | null;
}

export function useWebSocket(contentId: string | null): UseWebSocketResult {
  const [status, setStatus] = useState<ConnectionStatus>('disconnected');
  const [lastEvent, setLastEvent] = useState<WSInboundEvent | null>(null);
  const unsubscribeRef = useRef<(() => void) | null>(null);

  const subscriber = useRef<WSSubscriber>({
    onEvent: (event: WSInboundEvent) => {
      setLastEvent(event);
    },
    onStatusChange: (newStatus: ConnectionStatus) => {
      setStatus(newStatus);
    },
  });

  useEffect(() => {
    if (!contentId) return;

    setStatus('connecting');
    setLastEvent(null);

    unsubscribeRef.current = wsService.subscribe(contentId, subscriber.current);

    return () => {
      if (unsubscribeRef.current) {
        unsubscribeRef.current();
        unsubscribeRef.current = null;
      }
      setStatus('disconnected');
      setLastEvent(null);
    };
  }, [contentId]);

  return { status, lastEvent };
}

export function useMultipleWebSockets(contentIds: string[]): Map<string, ConnectionStatus> {
  const [statuses, setStatuses] = useState<Map<string, ConnectionStatus>>(() => new Map());

  const cleanupRef = useRef<Map<string, () => void>>(new Map());

  useEffect(() => {
    const currentIds = new Set(contentIds);
    const cleanup = cleanupRef.current;

    // Unsubscribe from removed IDs
    for (const [id, unsub] of cleanup) {
      if (!currentIds.has(id)) {
        unsub();
        cleanup.delete(id);
        setStatuses((prev) => {
          const next = new Map(prev);
          next.delete(id);
          return next;
        });
      }
    }

    // Subscribe to new IDs
    for (const id of contentIds) {
      if (!cleanup.has(id)) {
        const sub: WSSubscriber = {
          onEvent: () => {},
          onStatusChange: (s) => {
            setStatuses((prev) => {
              const next = new Map(prev);
              next.set(id, s);
              return next;
            });
          },
        };
        const unsub = wsService.subscribe(id, sub);
        cleanup.set(id, unsub);
      }
    }

    return () => {
      for (const [, unsub] of cleanup) {
        unsub();
      }
      cleanup.clear();
    };
  }, [contentIds]);

  return statuses;
}
