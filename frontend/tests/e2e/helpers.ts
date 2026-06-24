import type { Page } from '@playwright/test';
import { expect } from '@playwright/test';

export function uuid(): string {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
    const r = (Math.random() * 16) | 0;
    return (c === 'x' ? r : (r & 0x3) | 0x8).toString(16);
  });
}

export function timestamp(): string {
  return new Date().toISOString();
}

export function uniqueName(prefix: string): string {
  return `${prefix}-${Date.now()}-${Math.random().toString(36).slice(2, 6)}`;
}

interface GraphQLStub {
  operationName: string;
  data: Record<string, unknown>;
}

export function createGraphQLMockHandler(stubs: GraphQLStub[]) {
  return async (route: ReturnType<typeof page.route>) => {
    const request = route.request();
    if (request.method() !== 'POST') {
      await route.continue();
      return;
    }
    const postData = request.postDataJSON() as {
      operationName?: string;
      query?: string;
      variables?: Record<string, unknown>;
    };
    const opName = postData.operationName ?? '';
    const stub = stubs.find((s) => s.operationName === opName);
    if (stub) {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ data: stub.data }),
      });
    } else {
      await route.continue();
    }
  };
}

export function mockDataForError(operationName: string, message: string): GraphQLStub {
  return {
    operationName,
    data: {} as Record<string, unknown>,
  };
}

export async function createCampaign(page: Page, name: string, description: string) {
  await page.goto('/');
  await page.waitForLoadState('networkidle');
  await page.getByRole('button', { name: '+ New Campaign' }).click();
  await page.fill('#campaign-name', name);
  await page.fill('#campaign-description', description);
  await page.getByRole('button', { name: 'Create', exact: true }).click();
  await page.waitForLoadState('networkidle');
}

export async function createContentPiece(
  page: Page,
  headline: string,
  description: string,
) {
  await page.getByRole('button', { name: '+ New Piece' }).click();
  await page.fill('#content-headline', headline);
  await page.fill('#content-description', description);
  await page.getByRole('button', { name: 'Create', exact: true }).click();
  await page.waitForLoadState('networkidle');
}

export async function toggleContentSelection(page: Page, headline: string) {
  await page.getByText(headline, { exact: false }).first().click();
}

export async function expectStateBadge(page: Page, label: string) {
  await expect(page.getByText(label, { exact: true })).toBeVisible();
}

export async function expectNoStateBadge(page: Page, label: string) {
  await expect(page.getByText(label, { exact: true })).toHaveCount(0);
}

export function campaignStub(id: string, name: string, description: string) {
  return {
    id,
    name,
    description,
    status: 'ACTIVE',
    createdAt: timestamp(),
    updatedAt: timestamp(),
  };
}

export function contentStub(
  id: string,
  campaignId: string,
  headline: string,
  description: string,
  state: string,
  language = 'en',
) {
  return {
    id,
    campaignId,
    headline,
    description,
    body: '',
    language,
    state,
    originalId: null,
    createdAt: timestamp(),
    updatedAt: timestamp(),
  };
}

export function extractOpName(query: string): string {
  const match = query.match(/^\s*(?:query|mutation|subscription)\s+(\w+)/);
  return match?.[1] ?? '';
}

function parseGraphQLPostData(request: { postDataJSON(): Record<string, unknown> }): {
  operationName: string;
  variables: Record<string, unknown>;
} {
  const body = request.postDataJSON() as {
    operationName?: string;
    query?: string;
    variables?: Record<string, unknown>;
  };
  const opName =
    body.operationName || (body.query ? extractOpName(body.query) : '');
  return { operationName: opName, variables: body.variables ?? {} };
}

export type GraphQLMockHandler = Parameters<typeof import('@playwright/test')['test']['prototype'] extends { route: infer R } ? R : never>[1];

export function createRouteHandler(stubs: Record<string, Record<string, unknown>>) {
  return async (route: Parameters<GraphQLMockHandler>[0]) => {
    const req = route.request();
    if (req.method() !== 'POST') {
      await route.continue();
      return;
    }
    const { operationName } = parseGraphQLPostData(req);
    const stubData = stubs[operationName];
    if (stubData) {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ data: stubData }),
      });
    } else {
      await route.continue();
    }
  };
}

export function createErrorRouteHandler(errors: Record<string, { message: string }>) {
  return async (route: Parameters<GraphQLMockHandler>[0]) => {
    const req = route.request();
    if (req.method() !== 'POST') {
      await route.continue();
      return;
    }
    const { operationName } = parseGraphQLPostData(req);
    const error = errors[operationName];
    if (error) {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ errors: [error] }),
      });
    } else {
      await route.continue();
    }
  };
}

export async function createRouteStub(
  page: Page,
  stubs: Record<string, Record<string, unknown>>,
): Promise<void> {
  await page.route('**/graphql', createRouteHandler(stubs));
}

export const GRAPHQL_ENDPOINT = '**/graphql';
