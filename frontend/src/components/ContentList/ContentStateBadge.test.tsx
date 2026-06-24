import { render, screen } from '@testing-library/react';
import { ContentStateBadge } from './ContentStateBadge';
import type { ContentState } from '../../types/content';

describe('ContentStateBadge', () => {
  const cases: Array<{ state: ContentState; label: string; bgClass: string; textClass: string }> = [
    { state: 'DRAFT', label: 'Draft', bgClass: 'bg-gray-100', textClass: 'text-gray-700' },
    { state: 'SUGGESTED_BY_AI', label: 'Suggested', bgClass: 'bg-blue-100', textClass: 'text-blue-800' },
    { state: 'REVIEWED', label: 'Reviewed', bgClass: 'bg-yellow-100', textClass: 'text-yellow-800' },
    { state: 'APPROVED', label: 'Approved', bgClass: 'bg-emerald-100', textClass: 'text-emerald-800' },
    { state: 'REJECTED', label: 'Rejected', bgClass: 'bg-red-100', textClass: 'text-red-800' },
  ];

  it.each(cases)('renders $label with correct styling for $state', ({ state, label, bgClass, textClass }) => {
    render(<ContentStateBadge state={state} />);
    const badge = screen.getByText(label);
    expect(badge).toBeInTheDocument();
    expect(badge.className).toContain(bgClass);
    expect(badge.className).toContain(textClass);
  });
});
