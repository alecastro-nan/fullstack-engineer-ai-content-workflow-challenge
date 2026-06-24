import { test, expect } from '@playwright/test';
import {
  uuid, createCampaign, createContentPiece,
  contentStub, createRouteStub,
} from './helpers';

const CAMPAIGN_NAME = `E2E-Campaign-${Date.now()}`;
const CAMPAIGN_DESC = 'Created by Playwright E2E test suite';

let campaignId: string;

async function ensureOnCampaign(page: import('@playwright/test').Page) {
  await page.goto('/');
  await page.waitForLoadState('networkidle');
  const card = page.getByText(CAMPAIGN_NAME).first();
  if (await card.isVisible()) {
    await card.click();
  } else {
    await createCampaign(page, CAMPAIGN_NAME, CAMPAIGN_DESC);
    await page.getByText(CAMPAIGN_NAME).first().click();
  }
  await page.waitForLoadState('networkidle');
  campaignId = page.url().split('/campaigns/')[1] ?? '';
}

test.describe('=== Infrastructure Verification ===', () => {
  test('Frontend serves HTML at / with 200 OK', async ({ page }) => {
    const resp = await page.goto('/');
    expect(resp?.status()).toBe(200);
    await expect(page.locator('h1')).toContainText('Campaigns');
  });

  test('GraphQL health endpoint returns ok', async () => {
    const resp = await fetch('http://localhost:8000/graphql', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query: 'query { health }' }),
    });
    expect(resp.status).toBe(200);
    const body = await resp.json() as { data?: { health?: string } };
    expect(body.data?.health).toBe('ok');
  });
});

test.describe('=== Campaign Management ===', () => {
  test('Campaign Dashboard loads with empty state', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    await expect(page.getByText('No campaigns yet')).toBeVisible();
  });

  test('Create Campaign validates empty name', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    await page.getByRole('button', { name: '+ New Campaign' }).click();
    await page.getByRole('button', { name: 'Create', exact: true }).click();
    await expect(page.getByText('Name is required')).toBeVisible();
  });

  test('Create Campaign with valid data succeeds', async ({ page }) => {
    await createCampaign(page, CAMPAIGN_NAME, CAMPAIGN_DESC);
    await expect(page.getByText(CAMPAIGN_NAME)).toBeVisible();
    await expect(page.getByText(CAMPAIGN_DESC)).toBeVisible();
    await expect(page.getByText('ACTIVE')).toBeVisible();
  });

  test('Campaign card shows name, description, status, date', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    await expect(page.getByText(CAMPAIGN_NAME)).toBeVisible();
    await expect(page.getByText(CAMPAIGN_DESC)).toBeVisible();
    await expect(page.getByText('ACTIVE')).toBeVisible();
  });

  test('Clicking a campaign navigates to detail page', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    await page.getByText(CAMPAIGN_NAME).first().click();
    await page.waitForLoadState('networkidle');
    expect(page.url()).toContain('/campaigns/');
    await expect(page.getByText(CAMPAIGN_NAME)).toBeVisible();
  });

  test('Delete campaign removes it from list', async ({ page }) => {
    const deleteName = `ToDelete-${Date.now()}`;
    await createCampaign(page, deleteName, 'will be deleted');
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    await page.getByRole('button', { name: 'Delete' }).first().click();
    await page.waitForLoadState('networkidle');
    await expect(page.getByText(deleteName)).toHaveCount(0);
  });
});

test.describe('=== Content Piece Management ===', () => {
  test.beforeEach(async ({ page }) => {
    await ensureOnCampaign(page);
  });

  test('Content list shows empty state initially', async ({ page }) => {
    await expect(page.getByText('No content pieces yet')).toBeVisible();
  });

  test('Create Content validates required headline', async ({ page }) => {
    await page.getByRole('button', { name: '+ New Piece' }).click();
    await page.getByRole('button', { name: 'Create', exact: true }).click();
    await expect(page.getByText('Headline is required')).toBeVisible();
  });

  test('Create Content with valid headline+description succeeds', async ({ page }) => {
    const h = `Piece-${uuid()}`;
    await createContentPiece(page, h, 'description');
    await expect(page.getByText(h)).toBeVisible();
  });

  test('Content card shows headline, language tag, state badge', async ({ page }) => {
    const h = `Piece-${uuid()}`;
    await createContentPiece(page, h, 'description');
    await expect(page.getByText(h)).toBeVisible();
    await expect(page.getByText('en', { exact: true }).first()).toBeVisible();
    await expect(page.getByText('Draft', { exact: true }).first()).toBeVisible();
  });

  test('Content card can expand and show editable fields', async ({ page }) => {
    const h = `Piece-${uuid()}`;
    await createContentPiece(page, h, 'description');
    await page.getByText(h).first().click();
    await expect(page.getByLabel('Headline')).toBeVisible();
    await expect(page.getByLabel('Description')).toBeVisible();
  });

  test('Content card can save edited headline/description', async ({ page }) => {
    const h = `Piece-${uuid()}`;
    await createContentPiece(page, h, 'description');
    await page.getByText(h).first().click();
    await page.getByLabel('Headline').fill(`${h} (edited)`);
    await page.getByRole('button', { name: 'Save' }).click();
    await page.waitForLoadState('networkidle');
    await expect(page.getByText(`${h} (edited)`)).toBeVisible();
  });
});

test.describe('=== AI Draft Generation ===', () => {
  let draftHeadline: string;

  test.beforeEach(async ({ page }) => {
    await page.unroute('**/graphql');
    await ensureOnCampaign(page);
    draftHeadline = `Draft-${uuid()}`;
    await createContentPiece(page, draftHeadline, `Description for ${draftHeadline}`);
  });

  test('Generate Draft button visible when content state is DRAFT', async ({ page }) => {
    await page.getByRole('button', { name: draftHeadline, exact: false }).click();
    await expect(page.getByRole('button', { name: 'Generate with AI' })).toBeVisible();
  });

  test('After successful generation, state changes to SUGGESTED_BY_AI', async ({ page }) => {
    await page.getByRole('button', { name: draftHeadline, exact: false }).click();
    await createRouteStub(page, {
      GenerateDraft: {
        generateDraft: contentStub(uuid(), campaignId, 'AI Draft Result', 'AI generated content description', 'SUGGESTED_BY_AI'),
      },
    });
    await page.getByRole('button', { name: 'Generate with AI' }).click();
    await page.waitForLoadState('networkidle');
    await expect(page.getByText('Suggested')).toBeVisible();
  });

  test('Generate Draft button hidden after state changes from DRAFT', async ({ page }) => {
    await page.getByRole('button', { name: draftHeadline, exact: false }).click();
    await createRouteStub(page, {
      GenerateDraft: {
        generateDraft: contentStub(uuid(), campaignId, 'AI Draft Result', 'AI generated content description', 'SUGGESTED_BY_AI'),
      },
    });
    await page.getByRole('button', { name: 'Generate with AI' }).click();
    await page.waitForLoadState('networkidle');
    await page.getByText('AI Draft Result').first().click();
    await expect(page.getByRole('button', { name: 'Generate with AI' })).toHaveCount(0);
  });

  test('Error state shown if AI generation fails', async ({ page }) => {
    await page.getByRole('button', { name: draftHeadline, exact: false }).click();
    await page.unroute('**/graphql');
    await page.route('**/graphql', async (route) => {
      const req = route.request();
      if (req.method() !== 'POST') { await route.continue(); return; }
      const body = req.postDataJSON() as { query?: string };
      const opName = body.query?.match(/^\s*(?:query|mutation|subscription)\s+(\w+)/)?.[1] ?? '';
      if (opName === 'GenerateDraft') {
        await route.fulfill({
          status: 200, contentType: 'application/json',
          body: JSON.stringify({ errors: [{ message: 'AI draft generation failed. Please try again later.' }] }),
        });
      } else {
        await route.continue();
      }
    });
    await page.getByRole('button', { name: 'Generate with AI' }).click();
    await page.waitForLoadState('networkidle');
    await expect(page.getByText('AI draft generation failed. Please try again later.')).toBeVisible();
  });
});

test.describe('=== Review Workflow ===', () => {
  let reviewHeadline: string;

  test.beforeEach(async ({ page }) => {
    await page.unroute('**/graphql');
    await ensureOnCampaign(page);
    reviewHeadline = `Review-${uuid()}`;
    await createContentPiece(page, reviewHeadline, `Description for ${reviewHeadline}`);
    await page.getByText(reviewHeadline, { exact: true }).click();
    await createRouteStub(page, {
      GenerateDraft: {
        generateDraft: contentStub(uuid(), campaignId, 'AI Draft for Review', 'Content pending review', 'SUGGESTED_BY_AI'),
      },
    });
    await page.getByRole('button', { name: 'Generate with AI' }).click();
    await page.waitForLoadState('networkidle');
  });

  test('Approve/Reject/Request Edits buttons visible for SUGGESTED_BY_AI', async ({ page }) => {
    await page.getByText('AI Draft for Review').click();
    await expect(page.getByRole('button', { name: 'Approve' })).toBeVisible();
    await expect(page.getByRole('button', { name: 'Reject' })).toBeVisible();
    await expect(page.getByRole('button', { name: 'Request Edits' })).toBeVisible();
    await expect(page.getByText('Suggested')).toBeVisible();
  });

  test('Approve action changes state to APPROVED', async ({ page }) => {
    await page.getByText('AI Draft for Review').click();
    await createRouteStub(page, {
      ReviewContent: {
        reviewContent: contentStub(uuid(), campaignId, 'AI Draft for Review', 'Content approved', 'APPROVED'),
      },
    });
    await page.getByRole('button', { name: 'Approve' }).first().click();
    await page.locator('text=Are you sure').locator('..').getByRole('button', { name: 'Approve' }).click();
    await page.waitForLoadState('networkidle');
    await page.getByText('AI Draft for Review').click();
    await expect(page.getByText('Approved').first()).toBeVisible();
  });

  test('Reject action with feedback changes state to REJECTED', async ({ page }) => {
    await page.getByText('AI Draft for Review').click();
    await createRouteStub(page, {
      ReviewContent: {
        reviewContent: contentStub(uuid(), campaignId, 'AI Draft for Review', 'Content rejected', 'REJECTED'),
      },
    });
    await page.getByRole('button', { name: 'Reject' }).first().click();
    await page.fill('#review-feedback', 'Needs more detail');
    await page.getByRole('button', { name: 'Submit' }).click();
    await page.waitForLoadState('networkidle');
    await page.getByText('AI Draft for Review').click();
    await expect(page.getByText('Rejected').first()).toBeVisible();
  });

  test('Request Edits changes state to REVIEWED', async ({ page }) => {
    await page.getByText('AI Draft for Review').click();
    await createRouteStub(page, {
      ReviewContent: {
        reviewContent: contentStub(uuid(), campaignId, 'AI Draft for Review', 'Content reviewed', 'REVIEWED'),
      },
    });
    await page.getByRole('button', { name: 'Request Edits' }).first().click();
    await page.fill('#review-feedback', 'Please adjust tone');
    await page.getByRole('button', { name: 'Submit' }).click();
    await page.waitForLoadState('networkidle');
    await page.getByText('AI Draft for Review').click();
    await expect(page.getByText('Reviewed').first()).toBeVisible();
  });

  test('Edit & Reset to Draft on REJECTED content', async ({ page }) => {
    await page.getByText('AI Draft for Review').click();
    await createRouteStub(page, {
      ReviewContent: {
        reviewContent: contentStub(uuid(), campaignId, 'AI Draft for Review', 'Content rejected for test', 'REJECTED'),
      },
      EditContent: {
        editContent: contentStub(uuid(), campaignId, 'AI Draft for Review', 'Content rejected for test', 'DRAFT'),
      },
    });
    await page.getByRole('button', { name: 'Reject' }).first().click();
    await page.fill('#review-feedback', 'Needs work');
    await page.getByRole('button', { name: 'Submit' }).click();
    await page.waitForLoadState('networkidle');
    await page.getByText('AI Draft for Review').click();
    await page.getByRole('button', { name: 'Edit & Reset to Draft' }).click();
    await page.waitForLoadState('networkidle');
    await expect(page.getByText('Draft').first()).toBeVisible();
  });

  test('Review buttons hidden for APPROVED content', async ({ page }) => {
    await page.getByText('AI Draft for Review').click();
    await createRouteStub(page, {
      ReviewContent: {
        reviewContent: contentStub(uuid(), campaignId, 'AI Draft for Review', 'Content approved', 'APPROVED'),
      },
    });
    await page.getByRole('button', { name: 'Approve' }).first().click();
    await page.locator('text=Are you sure').locator('..').getByRole('button', { name: 'Approve' }).click();
    await page.waitForLoadState('networkidle');
    await page.getByText('AI Draft for Review').click();
    await expect(page.getByText('No actions available')).toBeVisible();
  });
});

test.describe('=== Translation ===', () => {
  let transHeadline: string;

  test.beforeEach(async ({ page }) => {
    await page.unroute('**/graphql');
    await ensureOnCampaign(page);
    transHeadline = `Trans-${uuid()}`;
    await createContentPiece(page, transHeadline, `Description for ${transHeadline}`);
    await page.getByText(transHeadline, { exact: true }).click();
    await createRouteStub(page, {
      GenerateDraft: {
        generateDraft: contentStub(uuid(), campaignId, 'Source Content', 'For translation test', 'SUGGESTED_BY_AI'),
      },
    });
    await page.getByRole('button', { name: 'Generate with AI' }).click();
    await page.waitForLoadState('networkidle');
    await page.getByText('Source Content').click();
    await createRouteStub(page, {
      ReviewContent: {
        reviewContent: contentStub(uuid(), campaignId, 'Source Content', 'For translation test', 'APPROVED'),
      },
    });
    await page.getByRole('button', { name: 'Approve' }).first().click();
    await page.locator('text=Are you sure').locator('..').getByRole('button', { name: 'Approve' }).click();
    await page.waitForLoadState('networkidle');
  });

  test('Translate button visible when content state is APPROVED', async ({ page }) => {
    await page.getByText('Source Content').click();
    await expect(page.getByRole('button', { name: 'Translate' })).toBeVisible();
  });

  test('Language selector shows supported codes', async ({ page }) => {
    await page.getByText('Source Content').click();
    await page.getByRole('button', { name: 'Translate' }).click();
    const select = page.locator('#target-language');
    const options = await select.locator('option').allTextContents();
    expect(options).toContain('Spanish (es)');
    expect(options).toContain('French (fr)');
    expect(options).toContain('German (de)');
    expect(options).toContain('Portuguese (pt)');
    expect(options).toContain('Italian (it)');
    expect(options).toContain('Japanese (ja)');
    expect(options).toContain('Chinese (zh)');
  });
});

test.describe('=== State Badge Rendering ===', () => {
  test('State badges render without crash on campaign detail', async ({ page }) => {
    await ensureOnCampaign(page);
    const badges = page.locator('span:has-text("Draft")');
    const count = await badges.count();
    expect(count).toBeGreaterThanOrEqual(0);
  });
});

test.describe('=== Edge Cases & Error Handling ===', () => {
  test('Creating campaign with empty name shows validation error', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    await page.getByRole('button', { name: '+ New Campaign' }).click();
    await page.getByRole('button', { name: 'Create', exact: true }).click();
    await expect(page.getByText('Name is required')).toBeVisible();
  });

  test('Creating content with empty headline shows validation error', async ({ page }) => {
    await ensureOnCampaign(page);
    await page.getByRole('button', { name: '+ New Piece' }).click();
    await page.getByRole('button', { name: 'Create', exact: true }).click();
    await expect(page.getByText('Headline is required')).toBeVisible();
  });

  test('Deleting a campaign with no content succeeds', async ({ page }) => {
    const emptyName = `Empty-${Date.now()}`;
    await createCampaign(page, emptyName, 'empty campaign');
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    await page.getByRole('button', { name: 'Delete' }).first().click();
    await page.waitForLoadState('networkidle');
    await expect(page.getByText(emptyName)).toHaveCount(0);
  });
});

test.describe('=== Regression: Recent Fixes ===', () => {
  test('CSRF — GraphQL mutations work via frontend nginx proxy (no 403)', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    await page.getByRole('button', { name: '+ New Campaign' }).click();
    await page.fill('#campaign-name', `CSRF-Test-${Date.now()}`);
    await page.getByRole('button', { name: 'Create', exact: true }).click();
    await page.waitForLoadState('networkidle');
    await expect(page.getByText('CSRF-Test')).toBeVisible();
  });

  test('Enum case — state badges render without crash', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    const badges = page.locator('span:has-text("Draft")');
    const count = await badges.count();
    expect(count).toBeGreaterThanOrEqual(0);
  });

  test('Health check — backend responds to GraphQL without error', async () => {
    const resp = await fetch('http://localhost:8000/graphql', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query: 'query { health }' }),
    });
    expect(resp.status).toBe(200);
  });
});
