import { describe, it, expect, vi, beforeEach } from 'vitest';
import { NotFoundException } from '@nestjs/common';
import { CampaignService } from '../../src/campaign/campaign.service';

function createMockDatabaseService() {
  const mockDb = {
    insert: vi.fn(),
    select: vi.fn(),
    update: vi.fn(),
  };

  return {
    db: mockDb,
  };
}

describe('CampaignService', () => {
  let service: CampaignService;
  let mockDb: ReturnType<typeof createMockDatabaseService>['db'];

  beforeEach(() => {
    const mockDatabase = createMockDatabaseService();
    mockDb = mockDatabase.db;
    service = new CampaignService(mockDatabase as any);
  });

  describe('create', () => {
    it('should insert a campaign and return it', async () => {
      const dto = { name: 'Test Campaign', description: 'A test' };
      const expected = {
        id: 'uuid-1',
        name: 'Test Campaign',
        description: 'A test',
        status: 'active',
        isDeleted: false,
        createdAt: new Date(),
        updatedAt: new Date(),
      };

      const returningMock = vi.fn().mockResolvedValue([expected]);
      const valuesMock = vi.fn().mockReturnValue({ returning: returningMock });
      mockDb.insert.mockReturnValue({ values: valuesMock });

      const result = await service.create(dto);

      expect(result).toEqual(expected);
      expect(mockDb.insert).toHaveBeenCalled();
      expect(valuesMock).toHaveBeenCalledWith({
        name: 'Test Campaign',
        description: 'A test',
      });
    });

    it('should create campaign without optional description', async () => {
      const dto = { name: 'Minimal' };
      const expected = {
        id: 'uuid-2',
        name: 'Minimal',
        description: null,
        status: 'active',
        isDeleted: false,
        createdAt: new Date(),
        updatedAt: new Date(),
      };

      const returningMock = vi.fn().mockResolvedValue([expected]);
      const valuesMock = vi.fn().mockReturnValue({ returning: returningMock });
      mockDb.insert.mockReturnValue({ values: valuesMock });

      const result = await service.create(dto);

      expect(result).toEqual(expected);
      expect(valuesMock).toHaveBeenCalledWith({
        name: 'Minimal',
        description: null,
      });
    });
  });

  describe('findAll', () => {
    function setupMockSelect(result: any, total: number) {
      const countResult = Promise.resolve([{ total }]);
      const countWhereMock = vi.fn().mockReturnValue(countResult);
      const countFromMock = vi.fn().mockReturnValue({ where: countWhereMock });

      const itemsOffsetMock = vi.fn().mockResolvedValue(result);
      const itemsLimitMock = vi.fn().mockReturnValue({ offset: itemsOffsetMock });
      const itemsOrderByMock = vi.fn().mockReturnValue({ limit: itemsLimitMock });
      const itemsWhereMock = vi.fn().mockReturnValue({ orderBy: itemsOrderByMock });
      const itemsFromMock = vi.fn().mockReturnValue({ where: itemsWhereMock });

      mockDb.select
        .mockReturnValueOnce({ from: countFromMock })
        .mockReturnValueOnce({ from: itemsFromMock });
    }

    it('should return paginated campaigns', async () => {
      const items = [
        { id: 'uuid-1', name: 'Campaign 1', description: null, status: 'active', isDeleted: false, createdAt: new Date(), updatedAt: new Date() },
      ];

      setupMockSelect(items, 1);

      const result = await service.findAll(1, 10);

      expect(result.items).toHaveLength(1);
      expect(result.meta.total).toBe(1);
      expect(result.meta.page).toBe(1);
      expect(result.meta.limit).toBe(10);
      expect(result.meta.totalPages).toBe(1);
    });

    it('should return empty list when no campaigns', async () => {
      setupMockSelect([], 0);

      const result = await service.findAll(1, 10);

      expect(result.items).toHaveLength(0);
      expect(result.meta.total).toBe(0);
    });
  });

  describe('findOne', () => {
    it('should return a campaign by id', async () => {
      const id = 'uuid-1';
      const expected = {
        id,
        name: 'Test',
        description: null,
        status: 'active',
        isDeleted: false,
        createdAt: new Date(),
        updatedAt: new Date(),
      };

      const limitMock = vi.fn().mockResolvedValue([expected]);
      const whereMock = vi.fn().mockReturnValue({ limit: limitMock });
      const fromMock = vi.fn().mockReturnValue({ where: whereMock });
      mockDb.select.mockReturnValue({ from: fromMock });

      const result = await service.findOne(id);

      expect(result).toEqual(expected);
    });

    it('should throw NotFoundException when campaign not found', async () => {
      const limitMock = vi.fn().mockResolvedValue([]);
      const whereMock = vi.fn().mockReturnValue({ limit: limitMock });
      const fromMock = vi.fn().mockReturnValue({ where: whereMock });
      mockDb.select.mockReturnValue({ from: fromMock });

      await expect(service.findOne('non-existent')).rejects.toThrow(NotFoundException);
    });
  });

  describe('update', () => {
    it('should update and return the campaign', async () => {
      const id = 'uuid-1';
      const dto = { name: 'Updated' };
      const existing = {
        id,
        name: 'Original',
        description: null,
        status: 'active',
        isDeleted: false,
        createdAt: new Date(),
        updatedAt: new Date(),
      };

      const returningMock = vi.fn().mockResolvedValue([{ ...existing, name: 'Updated' }]);
      const whereMock2 = vi.fn().mockReturnValue({ returning: returningMock });
      const setMock = vi.fn().mockReturnValue({ where: whereMock2 });
      mockDb.update.mockReturnValue({ set: setMock });

      const limitMock = vi.fn().mockResolvedValue([existing]);
      const whereMock = vi.fn().mockReturnValue({ limit: limitMock });
      const fromMock = vi.fn().mockReturnValue({ where: whereMock });
      mockDb.select.mockReturnValue({ from: fromMock });

      const result = await service.update(id, dto);

      expect(result.name).toBe('Updated');
      expect(mockDb.update).toHaveBeenCalled();
    });

    it('should throw NotFoundException when updating non-existent campaign', async () => {
      const limitMock = vi.fn().mockResolvedValue([]);
      const whereMock = vi.fn().mockReturnValue({ limit: limitMock });
      const fromMock = vi.fn().mockReturnValue({ where: whereMock });
      mockDb.select.mockReturnValue({ from: fromMock });

      await expect(service.update('non-existent', { name: 'Nope' })).rejects.toThrow(NotFoundException);
    });
  });

  describe('remove', () => {
    it('should soft-delete a campaign', async () => {
      const id = 'uuid-1';
      const existing = {
        id,
        name: 'To Delete',
        description: null,
        status: 'active',
        isDeleted: false,
        createdAt: new Date(),
        updatedAt: new Date(),
      };

      const whereMock2 = vi.fn().mockResolvedValue(undefined);
      const setMock = vi.fn().mockReturnValue({ where: whereMock2 });
      mockDb.update.mockReturnValue({ set: setMock });

      const limitMock = vi.fn().mockResolvedValue([existing]);
      const whereMock = vi.fn().mockReturnValue({ limit: limitMock });
      const fromMock = vi.fn().mockReturnValue({ where: whereMock });
      mockDb.select.mockReturnValue({ from: fromMock });

      await service.remove(id);

      expect(mockDb.update).toHaveBeenCalled();
    });

    it('should throw NotFoundException when deleting non-existent campaign', async () => {
      const limitMock = vi.fn().mockResolvedValue([]);
      const whereMock = vi.fn().mockReturnValue({ limit: limitMock });
      const fromMock = vi.fn().mockReturnValue({ where: whereMock });
      mockDb.select.mockReturnValue({ from: fromMock });

      await expect(service.remove('non-existent')).rejects.toThrow(NotFoundException);
    });
  });
});
