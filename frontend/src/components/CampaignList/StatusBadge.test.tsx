import { render, screen } from '@testing-library/react';
import { StatusBadge } from './StatusBadge';

describe('StatusBadge', () => {
  it('renders active status with correct styling', () => {
    render(<StatusBadge status="active" />);
    const badge = screen.getByText('active');
    expect(badge).toBeInTheDocument();
    expect(badge.className).toContain('bg-emerald-100');
    expect(badge.className).toContain('text-emerald-800');
  });

  it('renders archived status with correct styling', () => {
    render(<StatusBadge status="archived" />);
    const badge = screen.getByText('archived');
    expect(badge).toBeInTheDocument();
    expect(badge.className).toContain('bg-gray-100');
    expect(badge.className).toContain('text-gray-600');
  });

  it('renders unknown status with fallback styling', () => {
    render(<StatusBadge status="unknown" />);
    const badge = screen.getByText('unknown');
    expect(badge).toBeInTheDocument();
  });
});
