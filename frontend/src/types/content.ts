export type ContentState =
  | 'draft'
  | 'suggested_by_ai'
  | 'reviewed'
  | 'approved'
  | 'rejected';

export interface ContentPiece {
  id: string;
  campaignId: string;
  headline: string;
  description: string;
  body: string;
  language: string;
  state: ContentState;
  originalId: string | null;
  createdAt: string;
  updatedAt: string;
}

export interface ContentPiecePage {
  items: ContentPiece[];
  totalCount: number;
  page: number;
  perPage: number;
}
