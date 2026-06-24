import { render, screen } from '@testing-library/react';
import { ContentList } from './ContentList';
import type { ContentPiece } from '../../types/content';

const mockPieces: ContentPiece[] = [
  {
    id: '1',
    campaignId: 'camp-1',
    headline: 'Piece One',
    description: 'Desc one',
    body: '',
    language: 'en',
    state: 'DRAFT',
    originalId: null,
    createdAt: '2025-01-01T00:00:00Z',
    updatedAt: '2025-01-02T00:00:00Z',
  },
  {
    id: '2',
    campaignId: 'camp-1',
    headline: 'Piece Two',
    description: 'Desc two',
    body: '',
    language: 'fr',
    state: 'APPROVED',
    originalId: null,
    createdAt: '2025-01-03T00:00:00Z',
    updatedAt: '2025-01-04T00:00:00Z',
  },
];

describe('ContentList', () => {
  it('renders list of content pieces', () => {
    render(
      <ContentList
        pieces={mockPieces}
        selectedId={null}
        onSelect={vi.fn()}
        onUpdate={vi.fn()}
        loading={false}
        onCreateClick={vi.fn()}
      />,
    );
    expect(screen.getByText('Piece One')).toBeInTheDocument();
    expect(screen.getByText('Piece Two')).toBeInTheDocument();
  });

  it('shows empty state when no pieces', () => {
    render(
      <ContentList
        pieces={[]}
        selectedId={null}
        onSelect={vi.fn()}
        onUpdate={vi.fn()}
        loading={false}
        onCreateClick={vi.fn()}
      />,
    );
    expect(screen.getByText('No content pieces yet')).toBeInTheDocument();
  });

  it('shows loading skeleton when loading', () => {
    render(
      <ContentList
        pieces={[]}
        selectedId={null}
        onSelect={vi.fn()}
        onUpdate={vi.fn()}
        loading={true}
        onCreateClick={vi.fn()}
      />,
    );
    const skeletons = document.querySelectorAll('.animate-pulse');
    expect(skeletons.length).toBe(3);
  });
});
