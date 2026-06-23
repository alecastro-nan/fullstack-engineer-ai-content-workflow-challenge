import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { TranslatePanel } from './TranslatePanel';

describe('TranslatePanel', () => {
  it('renders Translate button initially', () => {
    render(<TranslatePanel currentLanguage="en" onTranslate={vi.fn()} />);
    expect(screen.getByText('Translate')).toBeInTheDocument();
  });

  it('opens language selector when Translate is clicked', async () => {
    const user = userEvent.setup();
    render(<TranslatePanel currentLanguage="en" onTranslate={vi.fn()} />);
    await user.click(screen.getByText('Translate'));
    expect(screen.getByText('Target Language')).toBeInTheDocument();
    expect(screen.getByText('Start Translation')).toBeInTheDocument();
    expect(screen.getByText('Cancel')).toBeInTheDocument();
  });

  it('excludes current language from available options', async () => {
    const user = userEvent.setup();
    render(<TranslatePanel currentLanguage="es" onTranslate={vi.fn()} />);
    await user.click(screen.getByText('Translate'));
    const select = screen.getByRole('combobox');
    expect(select).toBeInTheDocument();
    expect(screen.queryByText('Spanish (es)')).not.toBeInTheDocument();
  });

  it('shows all languages except current one', async () => {
    const user = userEvent.setup();
    render(<TranslatePanel currentLanguage="en" onTranslate={vi.fn()} />);
    await user.click(screen.getByText('Translate'));
    expect(screen.getByText('Spanish (es)')).toBeInTheDocument();
    expect(screen.getByText('French (fr)')).toBeInTheDocument();
    expect(screen.getByText('German (de)')).toBeInTheDocument();
    expect(screen.getByText('Portuguese (pt)')).toBeInTheDocument();
    expect(screen.getByText('Italian (it)')).toBeInTheDocument();
    expect(screen.getByText('Japanese (ja)')).toBeInTheDocument();
    expect(screen.getByText('Chinese (zh)')).toBeInTheDocument();
  });

  it('disables Start Translation when no language selected', async () => {
    const user = userEvent.setup();
    render(<TranslatePanel currentLanguage="en" onTranslate={vi.fn()} />);
    await user.click(screen.getByText('Translate'));
    expect(screen.getByText('Start Translation')).toBeDisabled();
  });

  it('calls onTranslate with selected language', async () => {
    const onTranslate = vi.fn().mockResolvedValue(undefined);
    const user = userEvent.setup();
    render(<TranslatePanel currentLanguage="en" onTranslate={onTranslate} />);
    await user.click(screen.getByText('Translate'));
    await user.selectOptions(screen.getByRole('combobox'), 'es');
    await user.click(screen.getByText('Start Translation'));
    expect(onTranslate).toHaveBeenCalledWith('es');
  });

  it('shows error message when onTranslate fails', async () => {
    const onTranslate = vi.fn().mockRejectedValue(new Error('AI translation failed'));
    const user = userEvent.setup();
    render(<TranslatePanel currentLanguage="en" onTranslate={onTranslate} />);
    await user.click(screen.getByText('Translate'));
    await user.selectOptions(screen.getByRole('combobox'), 'fr');
    await user.click(screen.getByText('Start Translation'));
    expect(await screen.findByText('AI translation failed')).toBeInTheDocument();
  });

  it('closes panel on cancel', async () => {
    const user = userEvent.setup();
    render(<TranslatePanel currentLanguage="en" onTranslate={vi.fn()} />);
    await user.click(screen.getByText('Translate'));
    expect(screen.getByText('Target Language')).toBeInTheDocument();
    await user.click(screen.getByText('Cancel'));
    expect(screen.getByText('Translate')).toBeInTheDocument();
    expect(screen.queryByText('Target Language')).not.toBeInTheDocument();
  });
});
