import { useState } from 'react';
import type { ContentPiece } from '../../types/content';
import { ContentStateBadge } from './ContentStateBadge';

interface ContentPieceCardProps {
  content: ContentPiece;
  isSelected: boolean;
  onSelect: (id: string) => void;
  onUpdate: (id: string, headline: string, description: string) => Promise<void>;
}

export function ContentPieceCard({
  content,
  isSelected,
  onSelect,
  onUpdate,
}: ContentPieceCardProps) {
  const [headline, setHeadline] = useState(content.headline);
  const [description, setDescription] = useState(content.description);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

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
                className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
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
                className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
              />
            </div>
          </div>
          {error && (
            <p className="mt-2 text-xs text-red-600">{error}</p>
          )}
          <div className="mt-3 flex justify-end gap-2">
            <button
              type="button"
              onClick={handleCancel}
              className="rounded-md border border-gray-300 px-3 py-1.5 text-xs font-medium text-gray-700 transition-colors hover:bg-gray-50"
            >
              Cancel
            </button>
            <button
              type="button"
              onClick={handleSave}
              disabled={saving || !headline.trim()}
              className="rounded-md bg-blue-600 px-3 py-1.5 text-xs font-medium text-white transition-colors hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {saving ? 'Saving...' : 'Save'}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
