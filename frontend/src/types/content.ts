import type { ContentState } from './review';

export interface ContentPiece {
  id: string;
  campaignId: string;
  headline: string;
  description?: string;
  body?: string;
  language: string;
  state: ContentState;
  createdAt: string;
  updatedAt: string;
}
