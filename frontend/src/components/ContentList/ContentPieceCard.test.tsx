import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ContentPieceCard } from './ContentPieceCard';
import type { ContentPiece } from '../../types/content';

const mockContent: ContentPiece = {
  id: '1',
  campaignId: 'camp-1',
  headline: 'Test Headline',
  description: 'A test description',
  body: '',
  language: 'en',
  state: 'draft',
  originalId: null,
  createdAt: '2025-01-01T00:00:00Z',
  updatedAt: '2025-01-02T00:00:00Z',
};

describe('ContentPieceCard', () => {
  it('renders headline and language tag', () => {
    render(
      <ContentPieceCard
        content={mockContent}
        isSelected={false}
        onSelect={vi.fn()}
        onUpdate={vi.fn()}
      />,
    );
    expect(screen.getByText('Test Headline')).toBeInTheDocument();
    expect(screen.getByText('en')).toBeInTheDocument();
  });

  it('renders state badge', () => {
    render(
      <ContentPieceCard
        content={mockContent}
        isSelected={false}
        onSelect={vi.fn()}
        onUpdate={vi.fn()}
      />,
    );
    expect(screen.getByText('Draft')).toBeInTheDocument();
  });

  it('calls onSelect when card is clicked', async () => {
    const onSelect = vi.fn();
    const user = userEvent.setup();
    render(
      <ContentPieceCard
        content={mockContent}
        isSelected={false}
        onSelect={onSelect}
        onUpdate={vi.fn()}
      />,
    );
    await user.click(screen.getByText('Test Headline'));
    expect(onSelect).toHaveBeenCalledWith('1');
  });

  it('shows inline edit form when selected', () => {
    render(
      <ContentPieceCard
        content={mockContent}
        isSelected={true}
        onSelect={vi.fn()}
        onUpdate={vi.fn()}
      />,
    );
    expect(screen.getByDisplayValue('Test Headline')).toBeInTheDocument();
    expect(screen.getByDisplayValue('A test description')).toBeInTheDocument();
    expect(screen.getByText('Save')).toBeInTheDocument();
    expect(screen.getByText('Cancel')).toBeInTheDocument();
  });

  it('calls onUpdate with modified values on save', async () => {
    const onUpdate = vi.fn().mockResolvedValue(undefined);
    const user = userEvent.setup();
    render(
      <ContentPieceCard
        content={mockContent}
        isSelected={true}
        onSelect={vi.fn()}
        onUpdate={onUpdate}
      />,
    );
    const input = screen.getByDisplayValue('Test Headline');
    await user.clear(input);
    await user.type(input, 'Updated Headline');
    await user.click(screen.getByText('Save'));
    expect(onUpdate).toHaveBeenCalledWith('1', 'Updated Headline', 'A test description');
  });

  it('cancels edit and restores original values', async () => {
    const user = userEvent.setup();
    const onSelect = vi.fn();
    render(
      <ContentPieceCard
        content={mockContent}
        isSelected={true}
        onSelect={onSelect}
        onUpdate={vi.fn()}
      />,
    );
    const input = screen.getByDisplayValue('Test Headline');
    await user.clear(input);
    await user.type(input, 'Changed');
    await user.click(screen.getByText('Cancel'));
    expect(onSelect).toHaveBeenCalledWith('');
  });
});
