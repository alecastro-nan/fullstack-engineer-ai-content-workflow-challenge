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

export const CAMPAIGN_QUERY = `
  query Campaign($id: ID!) {
    campaign(id: $id) {
      id
      name
      description
      status
      createdAt
      updatedAt
    }
  }
`;

export const CONTENT_PIECES_QUERY = `
  query ContentPieces($campaignId: ID!, $page: Int!, $perPage: Int!) {
    contentPieces(campaignId: $campaignId, page: $page, perPage: $perPage) {
      items {
        id
        campaignId
        headline
        description
        body
        language
        state
        originalId
        createdAt
        updatedAt
      }
      totalCount
      page
      perPage
    }
  }
`;

export const CREATE_CONTENT_PIECE_MUTATION = `
  mutation CreateContentPiece($input: ContentPieceInput!) {
    createContentPiece(input: $input) {
      id
      campaignId
      headline
      description
      body
      language
      state
      originalId
      createdAt
      updatedAt
    }
  }
`;

export const UPDATE_CONTENT_PIECE_MUTATION = `
  mutation UpdateContentPiece($id: ID!, $input: ContentPieceUpdateInput!) {
    updateContentPiece(id: $id, input: $input) {
      id
      campaignId
      headline
      description
      body
      language
      state
      originalId
      createdAt
      updatedAt
    }
  }
`;

export const GENERATE_DRAFT_MUTATION = `
  mutation GenerateDraft($contentId: ID!) {
    generateDraft(contentId: $contentId) {
      id
      campaignId
      headline
      description
      body
      language
      state
      originalId
      createdAt
      updatedAt
    }
  }
`;

export const REVIEW_CONTENT_MUTATION = `
  mutation ReviewContent($contentId: ID!, $action: ReviewAction!, $feedback: String!) {
    reviewContent(contentId: $contentId, action: $action, feedback: $feedback) {
      id
      campaignId
      headline
      description
      body
      language
      state
      originalId
      createdAt
      updatedAt
    }
  }
`;

export const TRANSLATE_CONTENT_MUTATION = `
  mutation TranslateContent($contentId: ID!, $targetLanguage: String!) {
    translateContent(contentId: $contentId, targetLanguage: $targetLanguage) {
      id
      campaignId
      headline
      description
      body
      language
      state
      originalId
      createdAt
      updatedAt
    }
  }
`;

export const EDIT_CONTENT_MUTATION = `
  mutation EditContent($contentId: ID!, $headline: String, $description: String, $body: String) {
    editContent(contentId: $contentId, headline: $headline, description: $description, body: $body) {
      id
      campaignId
      headline
      description
      body
      language
      state
      originalId
      createdAt
      updatedAt
    }
  }
`;
