import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';
import { graphqlRequest } from '../services/api';
import type { Campaign } from '../types/campaign';
import { CampaignDashboard } from './CampaignDashboard';

vi.mock('../services/api', () => ({
  graphqlRequest: vi.fn(),
}));

const mockCampaign: Campaign = {
  id: '1',
  name: 'Test Campaign',
  description: 'A test description',
  status: 'active',
  createdAt: '2025-01-01T00:00:00Z',
  updatedAt: '2025-01-02T00:00:00Z',
};

const mockPageData = {
  campaigns: {
    items: [mockCampaign],
    totalCount: 1,
    page: 1,
    perPage: 20,
  },
};

function renderWithRouter(ui: React.ReactElement) {
  return render(<MemoryRouter>{ui}</MemoryRouter>);
}

describe('CampaignDashboard', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('shows loading skeleton while fetching campaigns', () => {
    vi.mocked(graphqlRequest).mockReturnValue(new Promise(() => {}));
    renderWithRouter(<CampaignDashboard />);
    const skeleton = document.querySelector('.animate-pulse');
    expect(skeleton).toBeInTheDocument();
  });

  it('renders empty state when no campaigns exist', async () => {
    vi.mocked(graphqlRequest).mockResolvedValue({
      campaigns: { items: [], totalCount: 0, page: 1, perPage: 20 },
    });
    renderWithRouter(<CampaignDashboard />);
    expect(await screen.findByText('No campaigns yet')).toBeInTheDocument();
  });

  it('renders campaign cards when data loads', async () => {
    vi.mocked(graphqlRequest).mockResolvedValue(mockPageData);
    renderWithRouter(<CampaignDashboard />);
    expect(await screen.findByText('Test Campaign')).toBeInTheDocument();
  });

  it('shows error message on fetch failure', async () => {
    vi.mocked(graphqlRequest).mockRejectedValue(new Error('Network error'));
    renderWithRouter(<CampaignDashboard />);
    expect(await screen.findByText('Network error')).toBeInTheDocument();
  });

  it('opens create campaign modal on button click', async () => {
    const user = userEvent.setup();
    vi.mocked(graphqlRequest).mockResolvedValue(mockPageData);
    renderWithRouter(<CampaignDashboard />);
    await screen.findByText('Test Campaign');

    await user.click(screen.getByText('+ New Campaign'));
    expect(screen.getByText('New Campaign')).toBeInTheDocument();
  });

  it('shows campaign count', async () => {
    vi.mocked(graphqlRequest).mockResolvedValue(mockPageData);
    renderWithRouter(<CampaignDashboard />);
    expect(await screen.findByText('1 campaign')).toBeInTheDocument();
  });
});
