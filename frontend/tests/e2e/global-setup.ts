import type { FullConfig } from '@playwright/test';
import http from 'http';

const GRAPHQL_URL = 'http://localhost:8000/graphql';
const FRONTEND_URL = 'http://localhost:5173';
const TIMEOUT_MS = 60_000;
const POLL_MS = 2_000;

async function waitForUrl(
  url: string,
  label: string,
  validate: (res: http.IncomingMessage) => boolean,
): Promise<void> {
  const start = Date.now();
  while (Date.now() - start < TIMEOUT_MS) {
    try {
      const code = await new Promise<number>((resolve, reject) => {
        const req = http.get(url, (res) => {
          res.resume();
          resolve(res.statusCode ?? 0);
        });
        req.on('error', reject);
        req.setTimeout(5_000, () => {
          req.destroy();
          reject(new Error('timeout'));
        });
      });
      if (validate({ statusCode: code } as http.IncomingMessage)) return;
    } catch {
      // retry
    }
    await new Promise((r) => setTimeout(r, POLL_MS));
  }
  throw new Error(`${label} at ${url} not ready after ${TIMEOUT_MS}ms`);
}

async function waitForGraphQL(): Promise<void> {
  const start = Date.now();
  while (Date.now() - start < TIMEOUT_MS) {
    try {
      const response = await fetch(GRAPHQL_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: 'query { health }' }),
      });
      if (response.ok) {
        const body = await response.json() as { data?: { health?: string } };
        if (body.data?.health === 'ok') return;
      }
    } catch {
      // retry
    }
    await new Promise((r) => setTimeout(r, POLL_MS));
  }
  throw new Error(`GraphQL at ${GRAPHQL_URL} not healthy after ${TIMEOUT_MS}ms`);
}

async function cleanDatabase(): Promise<void> {
  try {
    const listResp = await fetch(GRAPHQL_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        query: `query { campaigns(page: 1, perPage: 100) { items { id } } }`,
      }),
    });
    const listBody = await listResp.json() as { data?: { campaigns?: { items: Array<{ id: string }> } } };
    const ids = listBody.data?.campaigns?.items?.map((c) => c.id) ?? [];
    for (const id of ids) {
      await fetch(GRAPHQL_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: `mutation ($id: ID!) { deleteCampaign(id: $id) }`,
          variables: { id },
        }),
      });
    }
  } catch {
    // cleanup is best-effort
  }
}

export default async function globalSetup(_config: FullConfig): Promise<void> {
  await waitForUrl(FRONTEND_URL, 'Frontend', (res) => res.statusCode === 200);
  await waitForGraphQL();
  await cleanDatabase();
}
