import { useState } from 'react';
import type { ContentState } from '../../types/content';
import { ConfirmDialog } from './ConfirmDialog';

interface ReviewActionsProps {
  state: ContentState;
  onReview: (action: 'APPROVE' | 'REJECT' | 'REQUEST_EDITS', feedback: string) => Promise<void>;
  onEditContent: () => Promise<void>;
  disabled?: boolean;
}

type PendingAction = 'APPROVE' | 'REJECT' | 'REQUEST_EDITS' | null;

export function ReviewActions({ state, onReview, onEditContent, disabled }: ReviewActionsProps) {
  const [pendingAction, setPendingAction] = useState<PendingAction>(null);
  const [feedback, setFeedback] = useState('');
  const [feedbackVisible, setFeedbackVisible] = useState(false);
  const [confirmVisible, setConfirmVisible] = useState(false);
  const [mutating, setMutating] = useState(false);

  const isApprovable = state === 'suggested_by_ai' || state === 'reviewed';
  const isEditable = state === 'rejected';

  const handleConfirmApprove = async () => {
    setMutating(true);
    await onReview('APPROVE', '');
    setMutating(false);
    setConfirmVisible(false);
    setPendingAction(null);
  };

  const handleSubmitWithFeedback = async () => {
    if (!pendingAction) return;
    setMutating(true);
    await onReview(pendingAction, feedback);
    setMutating(false);
    setFeedbackVisible(false);
    setFeedback('');
    setPendingAction(null);
  };

  const openConfirm = (action: PendingAction) => {
    setPendingAction(action);
    if (action === 'REJECT' || action === 'REQUEST_EDITS') {
      setFeedbackVisible(true);
    } else {
      setConfirmVisible(true);
    }
  };

  const cancelAll = () => {
    setPendingAction(null);
    setFeedbackVisible(false);
    setConfirmVisible(false);
    setFeedback('');
  };

  return (
    <div className="mt-3 border-t border-gray-100 pt-3">
      {feedbackVisible && pendingAction && (
        <div className="mb-3">
          <label
            htmlFor="review-feedback"
            className="block text-xs font-medium text-gray-700"
          >
            {pendingAction === 'REJECT' ? 'Reason for rejection' : 'Feedback for edits'}
          </label>
          <textarea
            id="review-feedback"
            rows={2}
            value={feedback}
            onChange={(e) => setFeedback(e.target.value)}
            placeholder="Optional feedback..."
            disabled={mutating}
            className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 disabled:bg-gray-50"
          />
          <div className="mt-2 flex gap-2">
            <button
              type="button"
              onClick={handleSubmitWithFeedback}
              disabled={mutating}
              className="rounded-md bg-blue-600 px-3 py-1.5 text-xs font-medium text-white transition-opacity hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {mutating ? 'Submitting...' : 'Submit'}
            </button>
            <button
              type="button"
              onClick={cancelAll}
              disabled={mutating}
              className="rounded-md border border-gray-300 px-3 py-1.5 text-xs font-medium text-gray-700 transition-colors hover:bg-gray-50 disabled:cursor-not-allowed disabled:opacity-50"
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      <div className="flex flex-wrap gap-2">
        {isApprovable && !feedbackVisible && (
          <>
            <button
              type="button"
              onClick={() => openConfirm('APPROVE')}
              disabled={disabled || mutating}
              className="rounded-md bg-emerald-600 px-3 py-1.5 text-xs font-medium text-white transition-colors hover:bg-emerald-700 disabled:cursor-not-allowed disabled:opacity-50"
            >
              Approve
            </button>
            <button
              type="button"
              onClick={() => openConfirm('REJECT')}
              disabled={disabled || mutating}
              className="rounded-md bg-red-600 px-3 py-1.5 text-xs font-medium text-white transition-colors hover:bg-red-700 disabled:cursor-not-allowed disabled:opacity-50"
            >
              Reject
            </button>
            {state === 'suggested_by_ai' && (
              <button
                type="button"
                onClick={() => openConfirm('REQUEST_EDITS')}
                disabled={disabled || mutating}
                className="rounded-md border border-amber-300 bg-amber-50 px-3 py-1.5 text-xs font-medium text-amber-700 transition-colors hover:bg-amber-100 disabled:cursor-not-allowed disabled:opacity-50"
              >
                Request Edits
              </button>
            )}
          </>
        )}

        {isEditable && !feedbackVisible && (
          <button
            type="button"
            onClick={onEditContent}
            disabled={disabled || mutating}
            className="rounded-md bg-gray-600 px-3 py-1.5 text-xs font-medium text-white transition-colors hover:bg-gray-700 disabled:cursor-not-allowed disabled:opacity-50"
          >
            Edit &amp; Reset to Draft
          </button>
        )}

        {!isApprovable && !isEditable && state !== 'draft' && (
          <p className="text-xs text-gray-400 italic">No actions available</p>
        )}
      </div>

      {confirmVisible && pendingAction === 'APPROVE' && (
        <ConfirmDialog
          title="Approve Content"
          message="Are you sure you want to approve this content? This action cannot be undone."
          confirmLabel="Approve"
          confirmVariant="primary"
          onConfirm={handleConfirmApprove}
          onCancel={cancelAll}
          loading={mutating}
        />
      )}
    </div>
  );
}
