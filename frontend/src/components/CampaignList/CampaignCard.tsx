import { useNavigate } from 'react-router-dom';
import type { Campaign } from '../../types/campaign';
import { StatusBadge } from './StatusBadge';

interface CampaignCardProps {
  campaign: Campaign;
  onDelete: (id: string) => void;
}

export function CampaignCard({ campaign, onDelete }: CampaignCardProps) {
  const navigate = useNavigate();

  return (
    <div
      className="cursor-pointer rounded-lg border border-gray-200 bg-white p-5 shadow-sm transition-shadow hover:shadow-md"
      onClick={() => navigate(`/campaigns/${campaign.id}`)}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          navigate(`/campaigns/${campaign.id}`);
        }
      }}
    >
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <h3 className="text-lg font-semibold text-gray-900">
            {campaign.name}
          </h3>
          {campaign.description && (
            <p className="mt-1 text-sm text-gray-500 line-clamp-2">
              {campaign.description}
            </p>
          )}
        </div>
        <StatusBadge status={campaign.status} />
      </div>
      <div className="mt-4 flex items-center justify-between text-xs text-gray-400">
        <span>
          Created{' '}
          {new Date(campaign.createdAt).toLocaleDateString(undefined, {
            month: 'short',
            day: 'numeric',
            year: 'numeric',
          })}
        </span>
        <button
          type="button"
          onClick={(e) => {
            e.stopPropagation();
            onDelete(campaign.id);
          }}
          className="rounded px-2 py-1 text-gray-400 transition-colors hover:bg-red-50 hover:text-red-600"
        >
          Delete
        </button>
      </div>
    </div>
  );
}
