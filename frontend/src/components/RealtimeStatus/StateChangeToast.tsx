import { useEffect, useRef, useState } from 'react';
import type { StateChangeEvent } from '../../types/websocket';

const ACTION_LABELS: Record<string, string> = {
  GENERATE_AI: 'AI draft generated',
  APPROVE: 'Approved',
  REJECT: 'Rejected',
  REQUEST_EDITS: 'Edits requested',
  EDIT: 'Content edited',
  TRANSLATE: 'Translation created',
};

interface Toast {
  id: number;
  event: StateChangeEvent;
}

interface StateChangeToastProps {
  event: StateChangeEvent | null;
}

export function StateChangeToast({ event }: StateChangeToastProps) {
  const [toasts, setToasts] = useState<Toast[]>([]);
  const counterRef = useRef(0);

  useEffect(() => {
    if (!event) return;

    counterRef.current += 1;
    const id = counterRef.current;
    setToasts((prev) => [...prev, { id, event }]);

    const timer = setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id));
    }, 4000);

    return () => clearTimeout(timer);
  }, [event]);

  if (toasts.length === 0) return null;

  return (
    <div className="fixed bottom-4 right-4 z-50 flex flex-col gap-2">
      {toasts.map((toast) => (
        <div
          key={toast.id}
          className="animate-slide-up rounded-md border border-gray-200 bg-white px-4 py-3 shadow-lg"
        >
          <p className="text-sm font-medium text-gray-900">
            {toast.event.contentId.slice(0, 8)}...
          </p>
          <p className="text-xs text-gray-500">
            {ACTION_LABELS[toast.event.action] ?? toast.event.action}
          </p>
          <p className="text-xs text-gray-400">
            {toast.event.oldState} &rarr; {toast.event.newState}
          </p>
        </div>
      ))}
    </div>
  );
}
