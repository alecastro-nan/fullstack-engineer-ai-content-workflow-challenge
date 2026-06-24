import type { ContentState } from '../../types/content';

const STATE_STYLES: Partial<Record<ContentState, { bg: string; text: string; label: string }>> = {
  DRAFT: { bg: 'bg-gray-100', text: 'text-gray-700', label: 'Draft' },
  SUGGESTED_BY_AI: { bg: 'bg-blue-100', text: 'text-blue-800', label: 'Suggested' },
  REVIEWED: { bg: 'bg-yellow-100', text: 'text-yellow-800', label: 'Reviewed' },
  APPROVED: { bg: 'bg-emerald-100', text: 'text-emerald-800', label: 'Approved' },
  REJECTED: { bg: 'bg-red-100', text: 'text-red-800', label: 'Rejected' },
};

interface ContentStateBadgeProps {
  state: ContentState;
}

export function ContentStateBadge({ state }: ContentStateBadgeProps) {
  const styles = STATE_STYLES[state];
  if (!styles) {
    return (
      <span className="inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium bg-gray-100 text-gray-700">
        {state}
      </span>
    );
  }
  return (
    <span
      className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${styles.bg} ${styles.text}`}
    >
      {styles.label}
    </span>
  );
}
