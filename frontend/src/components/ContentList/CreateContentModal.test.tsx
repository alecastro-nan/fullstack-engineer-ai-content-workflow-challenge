import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { CreateContentModal } from './CreateContentModal';

describe('CreateContentModal', () => {
  it('does not render when open is false', () => {
    render(<CreateContentModal open={false} onClose={vi.fn()} onCreate={vi.fn()} />);
    expect(screen.queryByText('New Content Piece')).not.toBeInTheDocument();
  });

  it('renders form fields when open is true', () => {
    render(<CreateContentModal open={true} onClose={vi.fn()} onCreate={vi.fn()} />);
    expect(screen.getByText('New Content Piece')).toBeInTheDocument();
    expect(screen.getByLabelText('Headline *')).toBeInTheDocument();
    expect(screen.getByLabelText('Description')).toBeInTheDocument();
  });

  it('shows validation error when headline is empty on submit', async () => {
    const user = userEvent.setup();
    render(<CreateContentModal open={true} onClose={vi.fn()} onCreate={vi.fn()} />);
    await user.click(screen.getByText('Create'));
    expect(screen.getByText('Headline is required')).toBeInTheDocument();
  });

  it('calls onCreate with headline and description', async () => {
    const onCreate = vi.fn().mockResolvedValue(undefined);
    const user = userEvent.setup();
    render(<CreateContentModal open={true} onClose={vi.fn()} onCreate={onCreate} />);
    await user.type(screen.getByLabelText('Headline *'), 'Test Headline');
    await user.type(screen.getByLabelText('Description'), 'Test Description');
    await user.click(screen.getByText('Create'));
    expect(onCreate).toHaveBeenCalledWith('Test Headline', 'Test Description');
  });

  it('calls onClose when cancel is clicked', async () => {
    const onClose = vi.fn();
    const user = userEvent.setup();
    render(<CreateContentModal open={true} onClose={onClose} onCreate={vi.fn()} />);
    await user.click(screen.getByText('Cancel'));
    expect(onClose).toHaveBeenCalled();
  });

  it('displays error message when onCreate fails', async () => {
    const onCreate = vi.fn().mockRejectedValue(new Error('Creation failed'));
    const user = userEvent.setup();
    render(<CreateContentModal open={true} onClose={vi.fn()} onCreate={onCreate} />);
    await user.type(screen.getByLabelText('Headline *'), 'Test');
    await user.click(screen.getByText('Create'));
    expect(await screen.findByText('Creation failed')).toBeInTheDocument();
  });
});
