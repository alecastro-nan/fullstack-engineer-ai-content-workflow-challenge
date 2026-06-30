import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { CreateCampaignModal } from './CreateCampaignModal';

describe('CreateCampaignModal', () => {
  it('does not render when closed', () => {
    render(<CreateCampaignModal open={false} onClose={vi.fn()} onCreate={vi.fn()} />);
    expect(screen.queryByText('New Campaign')).not.toBeInTheDocument();
  });

  it('renders form when open', () => {
    render(<CreateCampaignModal open={true} onClose={vi.fn()} onCreate={vi.fn()} />);
    expect(screen.getByText('New Campaign')).toBeInTheDocument();
    expect(screen.getByLabelText('Name *')).toBeInTheDocument();
    expect(screen.getByLabelText('Description')).toBeInTheDocument();
  });

  it('shows validation error when name is empty', async () => {
    const user = userEvent.setup();
    render(<CreateCampaignModal open={true} onClose={vi.fn()} onCreate={vi.fn()} />);
    await user.click(screen.getByText('Create'));
    expect(screen.getByText('Name is required')).toBeInTheDocument();
  });

  it('calls onCreate with name and description', async () => {
    const onCreate = vi.fn().mockResolvedValue(undefined);
    const onClose = vi.fn();
    const user = userEvent.setup();

    render(<CreateCampaignModal open={true} onClose={onClose} onCreate={onCreate} />);

    await user.type(screen.getByLabelText('Name *'), 'New Campaign');
    await user.type(screen.getByLabelText('Description'), 'Campaign description');
    await user.click(screen.getByText('Create'));

    expect(onCreate).toHaveBeenCalledWith('New Campaign', 'Campaign description');
  });

  it('calls onClose when cancel is clicked', async () => {
    const onClose = vi.fn();
    const user = userEvent.setup();
    render(<CreateCampaignModal open={true} onClose={onClose} onCreate={vi.fn()} />);
    await user.click(screen.getByText('Cancel'));
    expect(onClose).toHaveBeenCalled();
  });

  it('displays error message when onCreate fails', async () => {
    const onCreate = vi.fn().mockRejectedValue(new Error('API Error'));
    const user = userEvent.setup();

    render(<CreateCampaignModal open={true} onClose={vi.fn()} onCreate={onCreate} />);

    await user.type(screen.getByLabelText('Name *'), 'Test');
    await user.click(screen.getByText('Create'));

    expect(await screen.findByText('API Error')).toBeInTheDocument();
  });
});
