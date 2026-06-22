export const CAMPAIGNS_QUERY = `
  query Campaigns($page: Int!, $perPage: Int!) {
    campaigns(page: $page, perPage: $perPage) {
      items {
        id
        name
        description
        status
        createdAt
        updatedAt
      }
      totalCount
      page
      perPage
    }
  }
`;

export const CREATE_CAMPAIGN_MUTATION = `
  mutation CreateCampaign($input: CampaignInput!) {
    createCampaign(input: $input) {
      id
      name
      description
      status
      createdAt
      updatedAt
    }
  }
`;

export const DELETE_CAMPAIGN_MUTATION = `
  mutation DeleteCampaign($id: ID!) {
    deleteCampaign(id: $id)
  }
`;
