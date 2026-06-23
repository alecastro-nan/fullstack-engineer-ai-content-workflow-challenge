import { useEffect, useState } from 'react';
import type { ContentPiece } from '../../types/content';
import { ContentStateBadge } from './ContentStateBadge';

interface ContentPieceCardProps {
  content: ContentPiece;
  isSelected: boolean;
  onSelect: (id: string) => void;
  onUpdate: (id: string, headline: string, description: string) => Promise<void>;
  onGenerateDraft?: (id: string) => Promise<void>;
  onReview?: (id: string, action: 'APPROVE' | 'REJECT') => Promise<void>;
}

export function ContentPieceCard({
  content,
  isSelected,
  onSelect,
  onUpdate,
  onGenerateDraft,
  onReview,
}: ContentPieceCardProps) {
  const [headline, setHeadline] = useState(content.headline);
  const [description, setDescription] = useState(content.description);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [generating, setGenerating] = useState(false);
  const [reviewing, setReviewing] = useState(false);

  useEffect(() => {
    setHeadline(content.headline);
    setDescription(content.description);
  }, [content.headline, content.description]);

  const isDraft = content.state === 'draft';
  const isSuggested = content.state === 'suggested_by_ai';

  const handleSave = async () => {
    if (!headline.trim()) return;
    setSaving(true);
    setError(null);
    try {
      await onUpdate(content.id, headline, description);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update');
    } finally {
      setSaving(false);
    }
  };

  const handleCancel = () => {
    setHeadline(content.headline);
    setDescription(content.description);
    setError(null);
    onSelect('');
  };

  const handleGenerateDraft = async () => {
    if (!onGenerateDraft) return;
    setGenerating(true);
    setError(null);
    try {
      await onGenerateDraft(content.id);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to generate draft');
    } finally {
      setGenerating(false);
    }
  };

  const handleReview = async (action: 'APPROVE' | 'REJECT') => {
    if (!onReview) return;
    setReviewing(true);
    setError(null);
    try {
      await onReview(content.id, action);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to review');
    } finally {
      setReviewing(false);
    }
  };

  return (
    <div
      className={`rounded-lg border bg-white p-4 shadow-sm transition-shadow ${
        isSelected ? 'border-blue-400 ring-1 ring-blue-400' : 'border-gray-200 hover:shadow-md'
      }`}
    >
      {!isSelected ? (
        <div
          className="cursor-pointer"
          onClick={() => onSelect(content.id)}
          role="button"
          tabIndex={0}
          onKeyDown={(e) => {
            if (e.key === 'Enter' || e.key === ' ') {
              onSelect(content.id);
            }
          }}
        >
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <h4 className="text-sm font-semibold text-gray-900">{content.headline}</h4>
              {content.description && (
                <p className="mt-0.5 text-xs text-gray-500 line-clamp-1">{content.description}</p>
              )}
            </div>
            <div className="ml-3 flex items-center gap-2">
              <span className="text-xs text-gray-400 uppercase">{content.language}</span>
              <ContentStateBadge state={content.state} />
            </div>
          </div>
          <p className="mt-2 text-xs text-gray-400">
            Created {new Date(content.createdAt).toLocaleDateString(undefined, {
              month: 'short',
              day: 'numeric',
              year: 'numeric',
            })}
          </p>
        </div>
      ) : (
        <div>
          <div className="mb-3 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="text-xs text-gray-400 uppercase">{content.language}</span>
              <ContentStateBadge state={content.state} />
            </div>
          </div>
          <div className="space-y-3">
            <div>
              <label
                htmlFor={`headline-${content.id}`}
                className="block text-xs font-medium text-gray-700"
              >
                Headline
              </label>
              <input
                id={`headline-${content.id}`}
                type="text"
                value={headline}
                onChange={(e) => setHeadline(e.target.value)}
                disabled={isSuggested}
                className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 disabled:bg-gray-50 disabled:text-gray-500"
              />
            </div>
            <div>
              <label
                htmlFor={`description-${content.id}`}
                className="block text-xs font-medium text-gray-700"
              >
                Description
              </label>
              <textarea
                id={`description-${content.id}`}
                rows={2}
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                disabled={isSuggested}
                className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 disabled:bg-gray-50 disabled:text-gray-500"
              />
            </div>
          </div>

          {isDraft && onGenerateDraft && (
            <div className="mt-3 border-t border-gray-100 pt-3">
              <button
                type="button"
                onClick={handleGenerateDraft}
                disabled={generating}
                className="w-full rounded-md bg-gradient-to-r from-purple-600 to-blue-600 px-4 py-2 text-sm font-medium text-white transition-opacity hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-50"
              >
                {generating ? (
                  <span className="flex items-center justify-center gap-2">
                    <svg className="h-4 w-4 animate-spin" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                    </svg>
                    Generating...
                  </span>
                ) : (
                  'Generate with AI'
                )}
              </button>
            </div>
          )}

          {isSuggested && onReview && (
            <div className="mt-3 border-t border-gray-100 pt-3">
              <p className="mb-2 text-xs font-medium text-gray-500">AI-generated draft — review:</p>
              <div className="flex gap-2">
                <button
                  type="button"
                  onClick={() => handleReview('APPROVE')}
                  disabled={reviewing}
                  className="flex-1 rounded-md bg-emerald-600 px-3 py-1.5 text-xs font-medium text-white transition-colors hover:bg-emerald-700 disabled:cursor-not-allowed disabled:opacity-50"
                >
                  {reviewing ? 'Processing...' : 'Approve'}
                </button>
                <button
                  type="button"
                  onClick={() => handleReview('REJECT')}
                  disabled={reviewing}
                  className="flex-1 rounded-md bg-red-600 px-3 py-1.5 text-xs font-medium text-white transition-colors hover:bg-red-700 disabled:cursor-not-allowed disabled:opacity-50"
                >
                  {reviewing ? 'Processing...' : 'Reject'}
                </button>
              </div>
            </div>
          )}

          {error && (
            <p className="mt-2 text-xs text-red-600">{error}</p>
          )}

          <div className="mt-3 flex justify-end gap-2">
            <button
              type="button"
              onClick={handleCancel}
              disabled={reviewing}
              className="rounded-md border border-gray-300 px-3 py-1.5 text-xs font-medium text-gray-700 transition-colors hover:bg-gray-50 disabled:cursor-not-allowed disabled:opacity-50"
            >
              Cancel
            </button>
            {!isSuggested && (
              <button
                type="button"
                onClick={handleSave}
                disabled={saving || !headline.trim()}
                className="rounded-md bg-blue-600 px-3 py-1.5 text-xs font-medium text-white transition-colors hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
              >
                {saving ? 'Saving...' : 'Save'}
              </button>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
