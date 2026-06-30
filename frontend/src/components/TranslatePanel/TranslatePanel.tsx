import { useState } from 'react';

interface TranslatePanelProps {
  currentLanguage: string;
  onTranslate: (targetLanguage: string) => Promise<void>;
}

const LANGUAGES: Record<string, string> = {
  es: 'Spanish',
  fr: 'French',
  de: 'German',
  pt: 'Portuguese',
  it: 'Italian',
  ja: 'Japanese',
  zh: 'Chinese',
};

export function TranslatePanel({ currentLanguage, onTranslate }: TranslatePanelProps) {
  const [open, setOpen] = useState(false);
  const [targetLanguage, setTargetLanguage] = useState('');
  const [translating, setTranslating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const availableLanguages = Object.entries(LANGUAGES).filter(([code]) => code !== currentLanguage);

  const handleTranslate = async () => {
    if (!targetLanguage) return;
    setTranslating(true);
    setError(null);
    try {
      await onTranslate(targetLanguage);
      setOpen(false);
      setTargetLanguage('');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Translation failed');
    } finally {
      setTranslating(false);
    }
  };

  return (
    <div className="mt-3 border-t border-gray-100 pt-3">
      {!open ? (
        <button
          type="button"
          onClick={() => setOpen(true)}
          className="w-full rounded-md bg-cyan-600 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-cyan-700"
        >
          Translate
        </button>
      ) : (
        <div className="space-y-3">
          <label htmlFor="target-language" className="block text-xs font-medium text-gray-700">
            Target Language
          </label>
          <select
            id="target-language"
            value={targetLanguage}
            onChange={(e) => setTargetLanguage(e.target.value)}
            disabled={translating}
            className="block w-full rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 disabled:bg-gray-50"
          >
            <option value="">Select a language...</option>
            {availableLanguages.map(([code, name]) => (
              <option key={code} value={code}>
                {name} ({code})
              </option>
            ))}
          </select>
          <div className="flex gap-2">
            <button
              type="button"
              onClick={handleTranslate}
              disabled={!targetLanguage || translating}
              className="rounded-md bg-cyan-600 px-4 py-1.5 text-xs font-medium text-white transition-colors hover:bg-cyan-700 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {translating ? (
                <span className="flex items-center gap-2">
                  <svg className="h-3.5 w-3.5 animate-spin" viewBox="0 0 24 24">
                    <circle
                      className="opacity-25"
                      cx="12"
                      cy="12"
                      r="10"
                      stroke="currentColor"
                      strokeWidth="4"
                      fill="none"
                    />
                    <path
                      className="opacity-75"
                      fill="currentColor"
                      d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
                    />
                  </svg>
                  Translating...
                </span>
              ) : (
                'Start Translation'
              )}
            </button>
            <button
              type="button"
              onClick={() => {
                setOpen(false);
                setTargetLanguage('');
                setError(null);
              }}
              disabled={translating}
              className="rounded-md border border-gray-300 px-4 py-1.5 text-xs font-medium text-gray-700 transition-colors hover:bg-gray-50 disabled:cursor-not-allowed disabled:opacity-50"
            >
              Cancel
            </button>
          </div>
          {error && <p className="text-xs text-red-600">{error}</p>}
        </div>
      )}
    </div>
  );
}
