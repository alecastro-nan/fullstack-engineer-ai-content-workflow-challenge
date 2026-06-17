import { describe, it, expect, beforeAll, afterAll } from 'vitest';
import { type INestApplication, ValidationPipe } from '@nestjs/common';
import { Test } from '@nestjs/testing';
import supertest from 'supertest';
import { AppModule } from '../../src/app.module';

describe('Campaign (e2e)', () => {
  let app: INestApplication;
  let createdId: string;

  beforeAll(async () => {
    const moduleFixture = await Test.createTestingModule({
      imports: [AppModule],
    }).compile();

    app = moduleFixture.createNestApplication();
    app.setGlobalPrefix('api');
    app.useGlobalPipes(
      new ValidationPipe({
        whitelist: true,
        forbidNonWhitelisted: true,
        transform: true,
      }),
    );
    await app.init();
  });

  afterAll(async () => {
    // Clean up test data
    if (createdId) {
      try {
        await supertest(app.getHttpServer()).delete(`/api/campaigns/${createdId}`);
      } catch {
        // ignore cleanup errors
      }
    }
    await app.close();
  });

  describe('POST /api/campaigns', () => {
    it('should create a campaign and return 201', async () => {
      const res = await supertest(app.getHttpServer())
        .post('/api/campaigns')
        .send({ name: 'E2E Test Campaign', description: 'Created during e2e' })
        .expect(201);

      expect(res.body).toHaveProperty('id');
      expect(res.body.name).toBe('E2E Test Campaign');
      expect(res.body.description).toBe('Created during e2e');
      expect(res.body.isDeleted).toBe(false);
      createdId = res.body.id;
    });
  });

  describe('GET /api/campaigns/:id', () => {
    it('should return a campaign by id', async () => {
      const res = await supertest(app.getHttpServer())
        .get(`/api/campaigns/${createdId}`)
        .expect(200);

      expect(res.body.name).toBe('E2E Test Campaign');
    });

    it('should return 404 when campaign not found', async () => {
      await supertest(app.getHttpServer())
        .get('/api/campaigns/00000000-0000-0000-0000-000000000000')
        .expect(404);
    });

    it('should return 400 for invalid UUID', async () => {
      await supertest(app.getHttpServer())
        .get('/api/campaigns/not-a-uuid')
        .expect(400);
    });
  });

  describe('GET /api/campaigns', () => {
    it('should return paginated list of campaigns', async () => {
      const res = await supertest(app.getHttpServer())
        .get('/api/campaigns?page=1&limit=10')
        .expect(200);

      expect(res.body).toHaveProperty('items');
      expect(res.body).toHaveProperty('meta');
      expect(Array.isArray(res.body.items)).toBe(true);
      expect(res.body.meta).toHaveProperty('total');
      expect(res.body.meta).toHaveProperty('page', 1);
      expect(res.body.meta).toHaveProperty('limit', 10);
    });
  });

  describe('PATCH /api/campaigns/:id', () => {
    it('should update a campaign and return 200', async () => {
      const res = await supertest(app.getHttpServer())
        .patch(`/api/campaigns/${createdId}`)
        .send({ name: 'Updated E2E Campaign' })
        .expect(200);

      expect(res.body.name).toBe('Updated E2E Campaign');
    });

    it('should return 404 when updating non-existent campaign', async () => {
      await supertest(app.getHttpServer())
        .patch('/api/campaigns/00000000-0000-0000-0000-000000000000')
        .send({ name: 'Nope' })
        .expect(404);
    });
  });

  describe('DELETE /api/campaigns/:id', () => {
    it('should soft-delete a campaign and return 204', async () => {
      await supertest(app.getHttpServer())
        .delete(`/api/campaigns/${createdId}`)
        .expect(204);
    });

    it('should return 404 when deleting non-existent campaign', async () => {
      await supertest(app.getHttpServer())
        .delete('/api/campaigns/00000000-0000-0000-0000-000000000000')
        .expect(404);
    });

    it('should return 400 for invalid UUID', async () => {
      await supertest(app.getHttpServer())
        .delete('/api/campaigns/not-a-uuid')
        .expect(400);
    });
  });
});
