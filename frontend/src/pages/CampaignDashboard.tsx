import { useCallback, useEffect, useRef, useState } from 'react';
import { CampaignCard, CreateCampaignModal } from '../components/CampaignList';
import { graphqlRequest } from '../services/api';
import {
  CAMPAIGNS_QUERY,
  CREATE_CAMPAIGN_MUTATION,
  DELETE_CAMPAIGN_MUTATION,
} from '../services/queries';
import type { Campaign } from '../types/campaign';

interface CampaignPageData {
  campaigns: CampaignPage;
}

interface CampaignPage {
  items: Campaign[];
  totalCount: number;
  page: number;
  perPage: number;
}

interface CreateCampaignData {
  createCampaign: Campaign;
}

export function CampaignDashboard() {
  const [campaigns, setCampaigns] = useState<Campaign[]>([]);
  const [totalCount, setTotalCount] = useState(0);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [modalOpen, setModalOpen] = useState(false);
  const perPage = 20;

  const mountedRef = useRef(true);
  const fetchIdRef = useRef(0);

  useEffect(() => {
    return () => {
      mountedRef.current = false;
    };
  }, []);

  const fetchCampaigns = useCallback(async (pageNum: number) => {
    const fetchId = ++fetchIdRef.current;
    setLoading(true);
    setError(null);
    try {
      const data = await graphqlRequest<CampaignPageData>(CAMPAIGNS_QUERY, {
        page: pageNum,
        perPage,
      });
      if (fetchId !== fetchIdRef.current || !mountedRef.current) return;
      setCampaigns(data.campaigns.items);
      setTotalCount(data.campaigns.totalCount);
      setPage(data.campaigns.page);
    } catch (err) {
      if (fetchId !== fetchIdRef.current || !mountedRef.current) return;
      setError(err instanceof Error ? err.message : 'Failed to load campaigns');
    } finally {
      if (fetchId === fetchIdRef.current && mountedRef.current) {
        setLoading(false);
      }
    }
  }, []);

  useEffect(() => {
    fetchCampaigns(1);
  }, [fetchCampaigns]);

  const handleCreate = useCallback(async (name: string, description: string) => {
    const data = await graphqlRequest<CreateCampaignData>(
      CREATE_CAMPAIGN_MUTATION,
      { input: { name, description } },
    );
    setCampaigns((prev) => [data.createCampaign, ...prev]);
    setTotalCount((prev) => prev + 1);
  }, []);

  const handleDelete = useCallback(async (id: string) => {
    try {
      await graphqlRequest<{ deleteCampaign: boolean }>(
        DELETE_CAMPAIGN_MUTATION,
        { id },
      );
      setCampaigns((prev) => prev.filter((c) => c.id !== id));
      setTotalCount((prev) => prev - 1);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : 'Failed to delete campaign',
      );
    }
  }, []);

  const totalPages = Math.ceil(totalCount / perPage);

  return (
    <div className="mx-auto max-w-4xl px-4 py-8">
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Campaigns</h1>
          <p className="mt-1 text-sm text-gray-500">
            {totalCount} campaign{totalCount !== 1 ? 's' : ''}
          </p>
        </div>
        <button
          type="button"
          onClick={() => setModalOpen(true)}
          className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-blue-700"
        >
          + New Campaign
        </button>
      </div>

      {error && (
        <div className="mb-4 rounded-md border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          {error}
        </div>
      )}

      {loading ? (
        <div className="space-y-4">
          {Array.from({ length: 3 }).map((_, i) => (
            <div
              key={i}
              className="h-28 animate-pulse rounded-lg border border-gray-200 bg-gray-100"
            />
          ))}
        </div>
      ) : campaigns.length === 0 ? (
        <div className="rounded-lg border-2 border-dashed border-gray-200 p-12 text-center">
          <p className="text-gray-500">No campaigns yet</p>
          <button
            type="button"
            onClick={() => setModalOpen(true)}
            className="mt-2 text-sm font-medium text-blue-600 hover:text-blue-700"
          >
            Create your first campaign
          </button>
        </div>
      ) : (
        <>
          <div className="space-y-4">
            {campaigns.map((campaign) => (
              <CampaignCard
                key={campaign.id}
                campaign={campaign}
                onDelete={handleDelete}
              />
            ))}
          </div>

          {totalPages > 1 && (
            <div className="mt-6 flex items-center justify-center gap-2">
              <button
                type="button"
                onClick={() => fetchCampaigns(page - 1)}
                disabled={page <= 1}
                className="rounded-md border border-gray-300 px-3 py-1.5 text-sm text-gray-700 transition-colors hover:bg-gray-50 disabled:cursor-not-allowed disabled:opacity-50"
              >
                Previous
              </button>
              <span className="text-sm text-gray-600">
                Page {page} of {totalPages}
              </span>
              <button
                type="button"
                onClick={() => fetchCampaigns(page + 1)}
                disabled={page >= totalPages}
                className="rounded-md border border-gray-300 px-3 py-1.5 text-sm text-gray-700 transition-colors hover:bg-gray-50 disabled:cursor-not-allowed disabled:opacity-50"
              >
                Next
              </button>
            </div>
          )}
        </>
      )}

      <CreateCampaignModal
        open={modalOpen}
        onClose={() => setModalOpen(false)}
        onCreate={handleCreate}
      />
    </div>
  );
}
