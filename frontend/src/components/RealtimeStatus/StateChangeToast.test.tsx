import { render, screen, act } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { StateChangeToast } from './StateChangeToast';
import type { StateChangeEvent } from '../../types/websocket';

describe('StateChangeToast', () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it('renders nothing when event is null', () => {
    const { container } = render(<StateChangeToast event={null} />);
    expect(container.firstChild).toBeNull();
  });

  it('renders toast when event is provided', () => {
    const event: StateChangeEvent = {
      type: 'state.change',
      contentId: 'abc-123-def',
      campaignId: 'camp-1',
      oldState: 'DRAFT',
      newState: 'SUGGESTED_BY_AI',
      action: 'GENERATE_AI',
      timestamp: '2025-01-01T00:00:00Z',
    };

    render(<StateChangeToast event={event} />);
    expect(screen.getByText('AI draft generated')).toBeInTheDocument();
    expect(screen.getByText(/abc-123/)).toBeInTheDocument();
  });

  it('shows correct action label for each action', () => {
    const events: Array<{ action: string; label: string }> = [
      { action: 'APPROVE', label: 'Approved' },
      { action: 'REJECT', label: 'Rejected' },
      { action: 'REQUEST_EDITS', label: 'Edits requested' },
      { action: 'EDIT', label: 'Content edited' },
      { action: 'TRANSLATE', label: 'Translation created' },
    ];

    for (const { action, label } of events) {
      const event: StateChangeEvent = {
        type: 'state.change',
        contentId: 'test-id',
        campaignId: 'camp-1',
        oldState: 'DRAFT',
        newState: 'SUGGESTED_BY_AI',
        action,
        timestamp: '2025-01-01T00:00:00Z',
      };
      const { unmount } = render(<StateChangeToast event={event} />);
      expect(screen.getByText(label)).toBeInTheDocument();
      unmount();
    }
  });

  it('shows state transition in toast', () => {
    const event: StateChangeEvent = {
      type: 'state.change',
      contentId: 'test-id',
      campaignId: 'camp-1',
      oldState: 'DRAFT',
      newState: 'APPROVED',
      action: 'APPROVE',
      timestamp: '2025-01-01T00:00:00Z',
    };

    render(<StateChangeToast event={event} />);
    expect(screen.getByText(/draft/i)).toBeInTheDocument();
    expect(screen.getByText(/approved/i)).toBeInTheDocument();
  });

  it('removes toast after 4 seconds', () => {
    const event: StateChangeEvent = {
      type: 'state.change',
      contentId: 'test-id',
      campaignId: 'camp-1',
      oldState: 'DRAFT',
      newState: 'APPROVED',
      action: 'APPROVE',
      timestamp: '2025-01-01T00:00:00Z',
    };

    render(<StateChangeToast event={event} />);
    expect(screen.getByText('Approved')).toBeInTheDocument();

    act(() => {
      vi.advanceTimersByTime(4000);
    });

    expect(screen.queryByText('Approved')).not.toBeInTheDocument();
  });
});
