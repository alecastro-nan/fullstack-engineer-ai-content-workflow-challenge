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

  it('shows Generate Draft button when content is draft and selected', () => {
    render(
      <ContentPieceCard
        content={mockContent}
        isSelected={true}
        onSelect={vi.fn()}
        onUpdate={vi.fn()}
        onGenerateDraft={vi.fn()}
      />,
    );
    expect(screen.getByText('Generate with AI')).toBeInTheDocument();
  });

  it('hides Generate Draft button when content is suggested_by_ai', () => {
    const suggestedContent = { ...mockContent, state: 'suggested_by_ai' as const };
    render(
      <ContentPieceCard
        content={suggestedContent}
        isSelected={true}
        onSelect={vi.fn()}
        onUpdate={vi.fn()}
        onGenerateDraft={vi.fn()}
      />,
    );
    expect(screen.queryByText('Generate with AI')).not.toBeInTheDocument();
  });

  it('calls onGenerateDraft when Generate button is clicked', async () => {
    const onGenerateDraft = vi.fn().mockResolvedValue(undefined);
    const user = userEvent.setup();
    render(
      <ContentPieceCard
        content={mockContent}
        isSelected={true}
        onSelect={vi.fn()}
        onUpdate={vi.fn()}
        onGenerateDraft={onGenerateDraft}
      />,
    );
    await user.click(screen.getByText('Generate with AI'));
    expect(onGenerateDraft).toHaveBeenCalledWith('1');
  });

  it('shows Approve, Reject, and Request Edits buttons when state is suggested_by_ai', () => {
    const suggestedContent = { ...mockContent, state: 'suggested_by_ai' as const };
    render(
      <ContentPieceCard
        content={suggestedContent}
        isSelected={true}
        onSelect={vi.fn()}
        onUpdate={vi.fn()}
        onReview={vi.fn()}
      />,
    );
    expect(screen.getByText('Approve')).toBeInTheDocument();
    expect(screen.getByText('Reject')).toBeInTheDocument();
    expect(screen.getByText('Request Edits')).toBeInTheDocument();
  });

  it('shows Approve and Reject buttons when state is reviewed (no Request Edits)', () => {
    const reviewedContent = { ...mockContent, state: 'reviewed' as const };
    render(
      <ContentPieceCard
        content={reviewedContent}
        isSelected={true}
        onSelect={vi.fn()}
        onUpdate={vi.fn()}
        onReview={vi.fn()}
      />,
    );
    expect(screen.getByText('Approve')).toBeInTheDocument();
    expect(screen.getByText('Reject')).toBeInTheDocument();
    expect(screen.queryByText('Request Edits')).not.toBeInTheDocument();
  });

  it('calls onReview with APPROVE after confirm dialog', async () => {
    const onReview = vi.fn().mockResolvedValue(undefined);
    const suggestedContent = { ...mockContent, state: 'suggested_by_ai' as const };
    const user = userEvent.setup();
    render(
      <ContentPieceCard
        content={suggestedContent}
        isSelected={true}
        onSelect={vi.fn()}
        onUpdate={vi.fn()}
        onReview={onReview}
      />,
    );
    await user.click(screen.getByText('Approve'));
    expect(screen.getByText((c) => c.includes('Are you sure you want to approve'))).toBeInTheDocument();
    await user.click(screen.getAllByText('Approve')[1]);
    expect(onReview).toHaveBeenCalledWith('1', 'APPROVE', '');
  });

  it('calls onReview with REJECT and feedback after submitting feedback', async () => {
    const onReview = vi.fn().mockResolvedValue(undefined);
    const suggestedContent = { ...mockContent, state: 'suggested_by_ai' as const };
    const user = userEvent.setup();
    render(
      <ContentPieceCard
        content={suggestedContent}
        isSelected={true}
        onSelect={vi.fn()}
        onUpdate={vi.fn()}
        onReview={onReview}
      />,
    );
    await user.click(screen.getByText('Reject'));
    const textarea = screen.getByPlaceholderText('Optional feedback...');
    await user.type(textarea, 'Not good enough');
    await user.click(screen.getByText('Submit'));
    expect(onReview).toHaveBeenCalledWith('1', 'REJECT', 'Not good enough');
  });

  it('calls onReview with REQUEST_EDITS and feedback', async () => {
    const onReview = vi.fn().mockResolvedValue(undefined);
    const suggestedContent = { ...mockContent, state: 'suggested_by_ai' as const };
    const user = userEvent.setup();
    render(
      <ContentPieceCard
        content={suggestedContent}
        isSelected={true}
        onSelect={vi.fn()}
        onUpdate={vi.fn()}
        onReview={onReview}
      />,
    );
    await user.click(screen.getByText('Request Edits'));
    const textarea = screen.getByPlaceholderText('Optional feedback...');
    await user.type(textarea, 'Make it shorter');
    await user.click(screen.getByText('Submit'));
    expect(onReview).toHaveBeenCalledWith('1', 'REQUEST_EDITS', 'Make it shorter');
  });

  it('shows Edit & Reset to Draft button when state is rejected', () => {
    const rejectedContent = { ...mockContent, state: 'rejected' as const };
    render(
      <ContentPieceCard
        content={rejectedContent}
        isSelected={true}
        onSelect={vi.fn()}
        onUpdate={vi.fn()}
        onEditContent={vi.fn()}
      />,
    );
    expect(screen.getByText('Edit & Reset to Draft')).toBeInTheDocument();
  });

  it('calls onEditContent when Edit button is clicked', async () => {
    const onEditContent = vi.fn().mockResolvedValue(undefined);
    const rejectedContent = { ...mockContent, state: 'rejected' as const };
    const user = userEvent.setup();
    render(
      <ContentPieceCard
        content={rejectedContent}
        isSelected={true}
        onSelect={vi.fn()}
        onUpdate={vi.fn()}
        onEditContent={onEditContent}
      />,
    );
    await user.click(screen.getByText('Edit & Reset to Draft'));
    expect(onEditContent).toHaveBeenCalledWith('1');
  });

  it('shows no actions message for approved content', () => {
    const approvedContent = { ...mockContent, state: 'approved' as const };
    render(
      <ContentPieceCard
        content={approvedContent}
        isSelected={true}
        onSelect={vi.fn()}
        onUpdate={vi.fn()}
        onReview={vi.fn()}
      />,
    );
    expect(screen.getByText('No actions available')).toBeInTheDocument();
  });
});
