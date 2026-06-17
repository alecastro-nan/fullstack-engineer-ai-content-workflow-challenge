# Skill: Test Patterns

## Purpose
Learn how to write mock-based AI tests, NestJS/FastAPI e2e tests, and React Testing Library component tests.

## When to Use
- When writing unit tests for AI service, campaign service, content service
- When writing integration/e2e tests for API endpoints
- When writing frontend component tests
- When running tests and checking coverage

## Steps

### 1. AI Service Mock Test
```typescript
// Key pattern: override provider in TestModule
const module = await Test.createTestingModule({
  providers: [AiService, { provide: OpenAI_PROVIDER, useValue: mockProvider }],
}).compile();

// Test: successful draft generation
// Test: provider failure triggers fallback
// Test: all providers fail → throws error
```

### 2. Controller E2E Test
```typescript
// Key pattern: use supertest + overrideProvider for AI mocks
await request(app.getHttpServer())
  .post('/api/campaigns')
  .send({ name: 'Test' })
  .expect(201);

// Override AiService to return mock data
// Test: create → verify response body and status
// Test: bad request → verify 400
```

### 3. React Component Test (Vitest + RTL)
```typescript
// Key pattern: render → query → fireEvent → assert
render(<Component prop={value} />);
expect(screen.getByText('Expected')).toBeInTheDocument();
fireEvent.click(screen.getByRole('button'));
expect(mockFn).toHaveBeenCalled();
```

### 4. Rules for All Tests
- Mock all AI providers — no real API calls
- Test both success and error paths (400, 404, 500)
- Each test file has a clear `describe` block per module
- Use `beforeEach` for clean state between tests
- No `console.log` in test output — use framework assertions

## Verification
- `pnpm test` passes with no warnings
- Coverage ≥80% for backend services
- Coverage ≥60% for frontend components
- No tests make real HTTP/AI calls
