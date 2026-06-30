export type ContentState = 'DRAFT' | 'SUGGESTED_BY_AI' | 'REVIEWED' | 'APPROVED' | 'REJECTED';

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
