import { useCallback, useEffect, useRef, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { graphqlRequest } from '../services/api';
import {
  CAMPAIGN_QUERY,
  CONTENT_PIECES_QUERY,
  CREATE_CONTENT_PIECE_MUTATION,
  UPDATE_CONTENT_PIECE_MUTATION,
} from '../services/queries';
import type { Campaign } from '../types/campaign';
import type { ContentPiece, ContentPiecePage } from '../types/content';
import { ContentList, CreateContentModal } from '../components/ContentList';

interface CampaignDetailData {
  campaign: Campaign | null;
}

export function CampaignDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [campaign, setCampaign] = useState<Campaign | null>(null);
  const [pieces, setPieces] = useState<ContentPiece[]>([]);
  const [selectedPieceId, setSelectedPieceId] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [createModalOpen, setCreateModalOpen] = useState(false);

  const mountedRef = useRef(true);
  useEffect(() => {
    return () => {
      mountedRef.current = false;
    };
  }, []);

  const fetchDetail = useCallback(async () => {
    if (!id) return;
    setLoading(true);
    setError(null);
    try {
      const [campaignData, piecesData] = await Promise.all([
        graphqlRequest<CampaignDetailData>(CAMPAIGN_QUERY, { id }),
        graphqlRequest<{ contentPieces: ContentPiecePage }>(CONTENT_PIECES_QUERY, {
          campaignId: id,
          page: 1,
          perPage: 50,
        }),
      ]);
      if (!mountedRef.current) return;

      if (!campaignData.campaign) {
        setError('Campaign not found');
        return;
      }

      setCampaign(campaignData.campaign);
      setPieces(piecesData.contentPieces.items);
    } catch (err) {
      if (!mountedRef.current) return;
      setError(err instanceof Error ? err.message : 'Failed to load campaign');
    } finally {
      if (mountedRef.current) setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    fetchDetail();
  }, [fetchDetail]);

  const handleCreate = useCallback(
    async (headline: string, description: string) => {
      if (!id) return;
      const data = await graphqlRequest<{ createContentPiece: ContentPiece }>(
        CREATE_CONTENT_PIECE_MUTATION,
        { input: { campaignId: id, headline, description } },
      );
      setPieces((prev) => [data.createContentPiece, ...prev]);
    },
    [id],
  );

  const handleUpdate = useCallback(
    async (pieceId: string, headline: string, description: string) => {
      const data = await graphqlRequest<{ updateContentPiece: ContentPiece }>(
        UPDATE_CONTENT_PIECE_MUTATION,
        { id: pieceId, input: { headline, description } },
      );
      setPieces((prev) =>
        prev.map((p) => (p.id === pieceId ? data.updateContentPiece : p)),
      );
      setSelectedPieceId(null);
    },
    [],
  );

  if (loading) {
    return (
      <div className="mx-auto max-w-4xl px-4 py-8">
        <div className="mb-6">
          <div className="h-8 w-48 animate-pulse rounded bg-gray-200" />
          <div className="mt-2 h-4 w-96 animate-pulse rounded bg-gray-200" />
        </div>
        <div className="space-y-4">
          {Array.from({ length: 3 }).map((_, i) => (
            <div key={i} className="h-20 animate-pulse rounded-lg border border-gray-200 bg-gray-100" />
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="mx-auto max-w-4xl px-4 py-8">
        <div className="rounded-md border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          {error}
        </div>
        <button
          type="button"
          onClick={() => navigate('/')}
          className="mt-4 text-sm font-medium text-blue-600 hover:text-blue-700"
        >
          &larr; Back to campaigns
        </button>
      </div>
    );
  }

  if (!campaign) {
    return (
      <div className="mx-auto max-w-4xl px-4 py-8">
        <p className="text-gray-500">Campaign not found</p>
        <button
          type="button"
          onClick={() => navigate('/')}
          className="mt-4 text-sm font-medium text-blue-600 hover:text-blue-700"
        >
          &larr; Back to campaigns
        </button>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-4xl px-4 py-8">
      <button
        type="button"
        onClick={() => navigate('/')}
        className="mb-6 text-sm text-gray-500 hover:text-gray-700"
      >
        &larr; Back to campaigns
      </button>

      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">{campaign.name}</h1>
        {campaign.description && (
          <p className="mt-1 text-sm text-gray-500">{campaign.description}</p>
        )}
      </div>

      <div className="mb-4 flex items-center justify-between">
        <h2 className="text-lg font-semibold text-gray-900">
          Content Pieces ({pieces.length})
        </h2>
        <button
          type="button"
          onClick={() => setCreateModalOpen(true)}
          className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-blue-700"
        >
          + New Piece
        </button>
      </div>

      <ContentList
        pieces={pieces}
        selectedId={selectedPieceId}
        onSelect={setSelectedPieceId}
        onUpdate={handleUpdate}
        loading={false}
        onCreateClick={() => setCreateModalOpen(true)}
      />

      <CreateContentModal
        open={createModalOpen}
        onClose={() => setCreateModalOpen(false)}
        onCreate={handleCreate}
      />
    </div>
  );
}
