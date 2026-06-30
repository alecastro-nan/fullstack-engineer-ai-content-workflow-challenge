import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';
import type { Campaign } from '../../types/campaign';
import { CampaignCard } from './CampaignCard';

const mockCampaign: Campaign = {
  id: '1',
  name: 'Test Campaign',
  description: 'A test description',
  status: 'active',
  createdAt: '2025-01-01T00:00:00Z',
  updatedAt: '2025-01-02T00:00:00Z',
};

function renderWithRouter(ui: React.ReactElement) {
  return render(<MemoryRouter>{ui}</MemoryRouter>);
}

describe('CampaignCard', () => {
  it('renders campaign name and description', () => {
    renderWithRouter(<CampaignCard campaign={mockCampaign} onDelete={vi.fn()} />);
    expect(screen.getByText('Test Campaign')).toBeInTheDocument();
    expect(screen.getByText('A test description')).toBeInTheDocument();
  });

  it('renders status badge', () => {
    renderWithRouter(<CampaignCard campaign={mockCampaign} onDelete={vi.fn()} />);
    expect(screen.getByText('active')).toBeInTheDocument();
  });

  it('calls onDelete when delete button is clicked', async () => {
    const onDelete = vi.fn();
    const user = userEvent.setup();
    renderWithRouter(<CampaignCard campaign={mockCampaign} onDelete={onDelete} />);
    await user.click(screen.getByText('Delete'));
    expect(onDelete).toHaveBeenCalledWith('1');
  });

  it('does not show description when not provided', () => {
    const campaignWithoutDesc: Campaign = {
      ...mockCampaign,
      description: undefined,
    };
    renderWithRouter(<CampaignCard campaign={campaignWithoutDesc} onDelete={vi.fn()} />);
    expect(screen.getByText('Test Campaign')).toBeInTheDocument();
  });
});
