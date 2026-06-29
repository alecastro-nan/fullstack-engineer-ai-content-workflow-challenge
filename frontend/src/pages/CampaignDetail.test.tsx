import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { CampaignDetail } from './CampaignDetail';
import { graphqlRequest } from '../services/api';
import type { Campaign } from '../types/campaign';
import type { ContentPiece } from '../types/content';

vi.mock('../services/api', () => ({
  graphqlRequest: vi.fn(),
}));

const mockCampaign: Campaign = {
  id: 'camp-1',
  name: 'Test Campaign',
  description: 'A test campaign',
  status: 'active',
  createdAt: '2025-01-01T00:00:00Z',
  updatedAt: '2025-01-02T00:00:00Z',
};

const mockPieces: ContentPiece[] = [
  {
    id: 'piece-1',
    campaignId: 'camp-1',
    headline: 'Piece One',
    description: 'Description one',
    body: '',
    language: 'en',
    state: 'DRAFT',
    originalId: null,
    createdAt: '2025-01-01T00:00:00Z',
    updatedAt: '2025-01-02T00:00:00Z',
  },
  {
    id: 'piece-2',
    campaignId: 'camp-1',
    headline: 'Piece Two',
    description: 'Description two',
    body: '',
    language: 'fr',
    state: 'APPROVED',
    originalId: null,
    createdAt: '2025-01-03T00:00:00Z',
    updatedAt: '2025-01-04T00:00:00Z',
  },
];

function renderWithRoute(route: string) {
  return render(
    <MemoryRouter initialEntries={[route]}>
      <Routes>
        <Route path="/campaigns/:id" element={<CampaignDetail />} />
        <Route path="/" element={<div>Dashboard</div>} />
      </Routes>
    </MemoryRouter>,
  );
}

describe('CampaignDetail', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders campaign header with name and description', async () => {
    vi.mocked(graphqlRequest)
      .mockResolvedValueOnce({ campaign: mockCampaign })
      .mockResolvedValueOnce({ contentPieces: { items: mockPieces, totalCount: 2, page: 1, perPage: 50 } });

    renderWithRoute('/campaigns/camp-1');

    expect(await screen.findByText('Test Campaign')).toBeInTheDocument();
    expect(screen.getByText('A test campaign')).toBeInTheDocument();
  });

  it('renders content piece list', async () => {
    vi.mocked(graphqlRequest)
      .mockResolvedValueOnce({ campaign: mockCampaign })
      .mockResolvedValueOnce({ contentPieces: { items: mockPieces, totalCount: 2, page: 1, perPage: 50 } });

    renderWithRoute('/campaigns/camp-1');

    expect(await screen.findByText('Piece One')).toBeInTheDocument();
    expect(await screen.findByText('Piece Two')).toBeInTheDocument();
  });

  it('shows error state when campaign not found', async () => {
    vi.mocked(graphqlRequest)
      .mockResolvedValueOnce({ campaign: null })
      .mockResolvedValueOnce({ contentPieces: { items: [], totalCount: 0, page: 1, perPage: 50 } });

    renderWithRoute('/campaigns/invalid');

    expect(await screen.findByText('Campaign not found')).toBeInTheDocument();
  });

  it('shows error message on fetch failure', async () => {
    vi.mocked(graphqlRequest)
      .mockRejectedValueOnce(new Error('Network error'));

    renderWithRoute('/campaigns/camp-1');

    expect(await screen.findByText('Network error')).toBeInTheDocument();
  });

  it('generates an AI draft and updates the piece state', async () => {
    const firstPiece = mockPieces[0];
    expect(firstPiece).toBeDefined();
    const updatedPiece: ContentPiece = {
      ...firstPiece,
      headline: 'AI Generated Headline',
      description: 'AI generated description',
      state: 'SUGGESTED_BY_AI',
    };

    vi.mocked(graphqlRequest)
      .mockResolvedValueOnce({ campaign: mockCampaign })
      .mockResolvedValueOnce({ contentPieces: { items: mockPieces, totalCount: 2, page: 1, perPage: 50 } })
      .mockResolvedValueOnce({ generateDraft: updatedPiece });

    const user = userEvent.setup();
    renderWithRoute('/campaigns/camp-1');

    await screen.findByText('Test Campaign');

    await user.click(screen.getByText('Piece One'));
    await user.click(screen.getByText('Generate with AI'));

    expect(await screen.findByDisplayValue('AI Generated Headline')).toBeInTheDocument();
    expect(screen.getByText('Suggested')).toBeInTheDocument();
  });

  it('creates a content piece and updates the list', async () => {
    const newPiece: ContentPiece = {
      id: 'piece-3',
      campaignId: 'camp-1',
      headline: 'New Piece',
      description: 'New description',
      body: '',
      language: 'en',
      state: 'DRAFT',
      originalId: null,
      createdAt: '2025-01-05T00:00:00Z',
      updatedAt: '2025-01-05T00:00:00Z',
    };

    vi.mocked(graphqlRequest)
      .mockResolvedValueOnce({ campaign: mockCampaign })
      .mockResolvedValueOnce({ contentPieces: { items: mockPieces, totalCount: 2, page: 1, perPage: 50 } })
      .mockResolvedValueOnce({ createContentPiece: newPiece });

    const user = userEvent.setup();
    renderWithRoute('/campaigns/camp-1');

    await screen.findByText('Test Campaign');

    await user.click(screen.getByText('+ New Piece'));
    await user.type(screen.getByLabelText('Headline *'), 'New Piece');
    await user.type(screen.getByLabelText('Description'), 'New description');
    await user.click(screen.getByText('Create'));

    await waitFor(() => {
      expect(screen.getByText('New Piece')).toBeInTheDocument();
    });
  });
});
