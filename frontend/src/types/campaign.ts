export type CampaignStatus = 'active' | 'archived';

export interface Campaign {
  id: string;
  name: string;
  description?: string;
  status: CampaignStatus;
  createdAt: string;
  updatedAt: string;
}
