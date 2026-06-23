import type { ContentPiece } from '../../types/content';
import { ContentPieceCard } from './ContentPieceCard';

interface ContentListProps {
  pieces: ContentPiece[];
  selectedId: string | null;
  onSelect: (id: string) => void;
  onUpdate: (id: string, headline: string, description: string) => Promise<void>;
  loading: boolean;
  onCreateClick: () => void;
}

export function ContentList({
  pieces,
  selectedId,
  onSelect,
  onUpdate,
  loading,
  onCreateClick,
}: ContentListProps) {
  if (loading) {
    return (
      <div className="space-y-4">
        {Array.from({ length: 3 }).map((_, i) => (
          <div
            key={i}
            className="h-20 animate-pulse rounded-lg border border-gray-200 bg-gray-100"
          />
        ))}
      </div>
    );
  }

  if (pieces.length === 0) {
    return (
      <div className="rounded-lg border-2 border-dashed border-gray-200 p-8 text-center">
        <p className="text-sm text-gray-500">No content pieces yet</p>
        <button
          type="button"
          onClick={onCreateClick}
          className="mt-2 text-xs font-medium text-blue-600 hover:text-blue-700"
        >
          Add your first piece
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {pieces.map((piece) => (
        <ContentPieceCard
          key={piece.id}
          content={piece}
          isSelected={selectedId === piece.id}
          onSelect={onSelect}
          onUpdate={onUpdate}
        />
      ))}
    </div>
  );
}
