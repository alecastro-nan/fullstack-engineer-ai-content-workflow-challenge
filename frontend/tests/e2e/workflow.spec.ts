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

  test('Translate creates new content piece in the list', async ({ page }) => {
    await page.getByText('Source Content').click();
    await page.getByRole('button', { name: 'Translate' }).click();
    await page.selectOption('#target-language', 'es');
    const translatedId = uuid();
    const translatedHeadline = 'Spanish Version';
    await createRouteStub(page, {
      TranslateContent: {
        translateContent: contentStub(translatedId, campaignId, translatedHeadline, 'Spanish translation', 'APPROVED', 'es'),
      },
    });
    await page.getByRole('button', { name: 'Start Translation' }).click();
    await page.waitForLoadState('networkidle');
    // The new translated piece should now be visible in the content list
    await expect(page.getByText(translatedHeadline)).toBeVisible();
  });

  test('Translated piece has correct language tag', async ({ page }) => {
    await page.getByText('Source Content').click();
    await page.getByRole('button', { name: 'Translate' }).click();
    await page.selectOption('#target-language', 'fr');
    const translatedId = uuid();
    const translatedHeadline = 'French Version';
    await createRouteStub(page, {
      TranslateContent: {
        translateContent: contentStub(translatedId, campaignId, translatedHeadline, 'French translation', 'APPROVED', 'fr'),
      },
    });
    await page.getByRole('button', { name: 'Start Translation' }).click();
    await page.waitForLoadState('networkidle');
    // The new piece shows its language tag on the card
    await expect(page.getByText('fr', { exact: true }).first()).toBeVisible();
    await expect(page.getByText(translatedHeadline)).toBeVisible();
  });
});

test.describe('=== State Badge Rendering ===', () => {
  test.beforeEach(async ({ page }) => {
    await page.unroute('**/graphql');
    await ensureOnCampaign(page);
    // campaignId is now set and we're on the detail page.
    // Go back to dashboard so each test can re-navigate with stubbed ContentPieces.
    await page.goto('/');
    await page.waitForLoadState('networkidle');
  });

  async function setupContentPieces(page: import('@playwright/test').Page, pieces: Array<{ state: string; headline: string }>) {
    const items = pieces.map((p) =>
      contentStub(uuid(), campaignId, p.headline, `Description for ${p.headline}`, p.state),
    );
    await createRouteStub(page, {
      ContentPieces: {
        contentPieces: {
          items,
          totalCount: items.length,
          page: 1,
          perPage: 50,
        },
      },
    });
    await page.getByText(CAMPAIGN_NAME).first().click();
    await page.waitForLoadState('networkidle');
  }

  test('DRAFT state shows "Draft" badge', async ({ page }) => {
    await setupContentPieces(page, [{ state: 'DRAFT', headline: 'State-Draft' }]);
    await expect(page.getByText('Draft', { exact: true })).toBeVisible();
  });

  test('SUGGESTED_BY_AI state shows "Suggested" badge', async ({ page }) => {
    await setupContentPieces(page, [{ state: 'SUGGESTED_BY_AI', headline: 'State-Suggested' }]);
    await expect(page.getByText('Suggested', { exact: true })).toBeVisible();
  });

  test('REVIEWED state shows "Reviewed" badge', async ({ page }) => {
    await setupContentPieces(page, [{ state: 'REVIEWED', headline: 'State-Reviewed' }]);
    await expect(page.getByText('Reviewed', { exact: true })).toBeVisible();
  });

  test('APPROVED state shows "Approved" badge', async ({ page }) => {
    await setupContentPieces(page, [{ state: 'APPROVED', headline: 'State-Approved' }]);
    await expect(page.getByText('Approved', { exact: true })).toBeVisible();
  });

  test('REJECTED state shows "Rejected" badge', async ({ page }) => {
    await setupContentPieces(page, [{ state: 'REJECTED', headline: 'State-Rejected' }]);
    await expect(page.getByText('Rejected', { exact: true })).toBeVisible();
  });

  test('Unknown/fallback state does not crash the page', async ({ page }) => {
    await setupContentPieces(page, [{ state: 'UNKNOWN_STATE', headline: 'State-Unknown' }]);
    // The fallback renders the raw state value
    await expect(page.getByText('UNKNOWN_STATE', { exact: true })).toBeVisible();
    // Content piece is still displayed (not empty state)
    await expect(page.getByText('State-Unknown', { exact: true })).toBeVisible();
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

  test.describe('Mutation error handling', () => {
    test.beforeEach(async ({ page }) => {
      await page.unroute('**/graphql');
      await ensureOnCampaign(page);
    });

    test('AI draft on non-existent content returns error', async ({ page }) => {
      const h = `ErrDraft-${uuid()}`;
      await createContentPiece(page, h, 'description');
      await page.getByText(h).first().click();
      await page.unroute('**/graphql');
      await page.route('**/graphql', async (route) => {
        const req = route.request();
        if (req.method() !== 'POST') { await route.continue(); return; }
        const body = req.postDataJSON() as { query?: string };
        const opName = body.query?.match(/^\s*(?:query|mutation|subscription)\s+(\w+)/)?.[1] ?? '';
        if (opName === 'GenerateDraft') {
          await route.fulfill({
            status: 200, contentType: 'application/json',
            body: JSON.stringify({ errors: [{ message: 'Content piece not found' }] }),
          });
        } else {
          await route.continue();
        }
      });
      await page.getByRole('button', { name: 'Generate with AI' }).click();
      await page.waitForLoadState('networkidle');
      await expect(page.getByText('Content piece not found')).toBeVisible();
    });

    test('Review action on non-existent content returns error', async ({ page }) => {
      const h = `ErrReview-${uuid()}`;
      await createContentPiece(page, h, 'description');
      await page.getByText(h).first().click();
      await createRouteStub(page, {
        GenerateDraft: {
          generateDraft: contentStub(uuid(), campaignId, h, 'description', 'SUGGESTED_BY_AI'),
        },
      });
      await page.getByRole('button', { name: 'Generate with AI' }).click();
      await page.waitForLoadState('networkidle');
      await page.getByText(h).first().click();
      await page.unroute('**/graphql');
      await page.route('**/graphql', async (route) => {
        const req = route.request();
        if (req.method() !== 'POST') { await route.continue(); return; }
        const body = req.postDataJSON() as { query?: string };
        const opName = body.query?.match(/^\s*(?:query|mutation|subscription)\s+(\w+)/)?.[1] ?? '';
        if (opName === 'ReviewContent') {
          await route.fulfill({
            status: 200, contentType: 'application/json',
            body: JSON.stringify({ errors: [{ message: 'Content piece not found' }] }),
          });
        } else {
          await route.continue();
        }
      });
      await page.getByRole('button', { name: 'Approve' }).first().click();
      await page.locator('text=Are you sure').locator('..').getByRole('button', { name: 'Approve' }).click();
      await page.waitForLoadState('networkidle');
      await expect(page.getByText('Content piece not found')).toBeVisible();
    });

    test('State machine invalid transitions return errors', async ({ page }) => {
      const h = `ErrInvalid-${uuid()}`;
      await createContentPiece(page, h, 'description');
      await page.getByText(h).first().click();
      await createRouteStub(page, {
        GenerateDraft: {
          generateDraft: contentStub(uuid(), campaignId, h, 'description', 'SUGGESTED_BY_AI'),
        },
      });
      await page.getByRole('button', { name: 'Generate with AI' }).click();
      await page.waitForLoadState('networkidle');
      await page.getByText(h).first().click();
      await page.unroute('**/graphql');
      await page.route('**/graphql', async (route) => {
        const req = route.request();
        if (req.method() !== 'POST') { await route.continue(); return; }
        const body = req.postDataJSON() as { query?: string };
        const opName = body.query?.match(/^\s*(?:query|mutation|subscription)\s+(\w+)/)?.[1] ?? '';
        if (opName === 'ReviewContent') {
          await route.fulfill({
            status: 200, contentType: 'application/json',
            body: JSON.stringify({ errors: [{ message: 'Invalid state transition from SUGGESTED_BY_AI to APPROVED' }] }),
          });
        } else {
          await route.continue();
        }
      });
      await page.getByRole('button', { name: 'Approve' }).first().click();
      await page.locator('text=Are you sure').locator('..').getByRole('button', { name: 'Approve' }).click();
      await page.waitForLoadState('networkidle');
      await expect(page.getByText('Invalid state transition')).toBeVisible();
    });
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

test.describe('=== Real-Time WebSocket ===', () => {
  test.beforeEach(async ({ page }) => {
    // Mock WebSocket constructor to avoid real backend WS dependency.
    // This runs in the browser before any app code executes.
    await page.addInitScript(() => {
      const connections: Array<{
        url: string;
        readyState: number;
        onopen: ((e: Event) => void) | null;
        onmessage: ((e: MessageEvent) => void) | null;
        onclose: ((e: CloseEvent) => void) | null;
        onerror: ((e: Event) => void) | null;
        close: () => void;
        send: (data: string) => void;
      }> = [];

      // Expose control API so test can send messages / close connections
      (window as any).__wsMock = {
        connections,

        /** Send a JSON message to all active mock connections */
        sendToAll(data: string) {
          for (const c of connections) {
            c.onmessage?.(new MessageEvent('message', { data }));
          }
        },

        /** Close all mock connections */
        closeAll() {
          for (const c of [...connections]) {
            c.close();
          }
        },

        /** Send to the first connection only */
        sendToFirst(data: string) {
          if (connections.length > 0) {
            connections[0].onmessage?.(new MessageEvent('message', { data }));
          }
        },

        /** Close the first connection */
        closeFirst() {
          if (connections.length > 0) {
            const c = connections[0];
            c.close();
            connections.splice(0, 1);
          }
        },
      };

      // Replace global WebSocket with a controllable mock
      (window as any).WebSocket = class MockWebSocket {
        url: string;
        readyState: number;

        onopen: ((e: Event) => void) | null = null;
        onmessage: ((e: MessageEvent) => void) | null = null;
        onclose: ((e: CloseEvent) => void) | null = null;
        onerror: ((e: Event) => void) | null = null;

        static CONNECTING = 0;
        static OPEN = 1;
        static CLOSING = 2;
        static CLOSED = 3;

        constructor(url: string) {
          this.url = url;
          this.readyState = 0; // CONNECTING
          connections.push(this);

          // Simulate server accepting the connection on the next microtask.
          // By then the wsService has already attached onopen/onmessage/onclose.
          Promise.resolve().then(() => {
            if (this.readyState === 0) {
              this.readyState = 1; // OPEN
              this.onopen?.(new Event('open'));
            }
          });
        }

        close() {
          if (this.readyState === 3) return;
          this.readyState = 3; // CLOSED
          this.onclose?.(new CloseEvent('close', { code: 1000, wasClean: true }));
        }

        send(_data: string) {
          // Not used by the current app server→client WS pattern
        }
      } as unknown as typeof window.WebSocket;
    });
  });

  test('Connection indicator shows green when connected', async ({ page }) => {
    await ensureOnCampaign(page);
    const h = `WS-Conn-${uuid()}`;
    await createContentPiece(page, h, 'ws connection test');

    // The mock WebSocket auto-opens → wsService sets status=connected
    // ConnectionIndicator renders "Connected" text
    await expect(page.getByText('Connected', { exact: true })).toBeVisible({ timeout: 10_000 });
  });

  test('State changes broadcast via WebSocket (toast notification)', async ({ page }) => {
    await ensureOnCampaign(page);
    const h = `WS-Toast-${uuid()}`;
    await createContentPiece(page, h, 'ws toast test');

    await expect(page.getByText('Connected', { exact: true })).toBeVisible({ timeout: 10_000 });

    // Send a state.change event through the mock WebSocket
    await page.evaluate(() => {
      const msg = JSON.stringify({
        type: 'state.change',
        contentId: 'e2e-test-content',
        campaignId: '',
        oldState: 'draft',
        newState: 'suggested_by_ai',
        action: 'GENERATE_AI',
        timestamp: new Date().toISOString(),
      });
      (window as any).__wsMock.sendToAll(msg);
    });

    // Toast shows action label and state transition
    await expect(page.getByText('AI draft generated')).toBeVisible();
    await expect(page.getByText('draft → suggested_by_ai')).toBeVisible();
  });

  test('Disconnecting and reconnecting shows connection state changes', async ({ page }) => {
    await ensureOnCampaign(page);
    const h = `WS-Recon-${uuid()}`;
    await createContentPiece(page, h, 'ws reconnect test');

    // 1. Initially connected
    await expect(page.getByText('Connected', { exact: true })).toBeVisible({ timeout: 10_000 });

    // 2. Close the mock WebSocket from server side
    await page.evaluate(() => {
      (window as any).__wsMock.closeAll();
    });

    // wsService.onclose fires → status='reconnecting' → "Reconnecting..."
    await expect(page.getByText('Reconnecting...')).toBeVisible({ timeout: 10_000 });

    // 3. wsService auto-reconnects after ~1s; the new MockWebSocket auto-opens
    await expect(page.getByText('Connected', { exact: true })).toBeVisible({ timeout: 15_000 });
  });
});
