import type { ContentState } from '../../types/content';

const STATE_STYLES: Record<ContentState, { bg: string; text: string; label: string }> = {
  draft: { bg: 'bg-gray-100', text: 'text-gray-700', label: 'Draft' },
  suggested_by_ai: { bg: 'bg-blue-100', text: 'text-blue-800', label: 'Suggested' },
  reviewed: { bg: 'bg-yellow-100', text: 'text-yellow-800', label: 'Reviewed' },
  approved: { bg: 'bg-emerald-100', text: 'text-emerald-800', label: 'Approved' },
  rejected: { bg: 'bg-red-100', text: 'text-red-800', label: 'Rejected' },
};

interface ContentStateBadgeProps {
  state: ContentState;
}

export function ContentStateBadge({ state }: ContentStateBadgeProps) {
  const styles = STATE_STYLES[state];
  return (
    <span
      className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${styles.bg} ${styles.text}`}
    >
      {styles.label}
    </span>
  );
}
