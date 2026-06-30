import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import type { ConnectionStatus } from '../../types/websocket';
import { ConnectionIndicator } from './ConnectionIndicator';

describe('ConnectionIndicator', () => {
  const cases: Array<{ status: ConnectionStatus; label: string }> = [
    { status: 'connected', label: 'Connected' },
    { status: 'connecting', label: 'Connecting...' },
    { status: 'reconnecting', label: 'Reconnecting...' },
    { status: 'disconnected', label: 'Disconnected' },
  ];

  it.each(cases)('renders $label for $status', ({ status, label }) => {
    render(<ConnectionIndicator status={status} />);
    expect(screen.getByText(label)).toBeInTheDocument();
  });

  it('renders a colored dot element', () => {
    const { container } = render(<ConnectionIndicator status="connected" />);
    const dot = container.querySelector('span');
    expect(dot).toBeInTheDocument();
  });
});
