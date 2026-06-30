import type { ConnectionStatus } from '../../types/websocket';

interface ConnectionIndicatorProps {
  status: ConnectionStatus;
}

const STATUS_CONFIG: Record<ConnectionStatus, { color: string; label: string }> = {
  connected: { color: 'bg-green-500', label: 'Connected' },
  connecting: { color: 'bg-yellow-500', label: 'Connecting...' },
  reconnecting: { color: 'bg-yellow-500', label: 'Reconnecting...' },
  disconnected: { color: 'bg-red-500', label: 'Disconnected' },
};

export function ConnectionIndicator({ status }: ConnectionIndicatorProps) {
  const config = STATUS_CONFIG[status];

  return (
    <div className="flex items-center gap-1.5 text-xs text-gray-500">
      <span className={`inline-block h-2 w-2 rounded-full ${config.color}`} title={config.label} />
      <span className="hidden sm:inline">{config.label}</span>
    </div>
  );
}
