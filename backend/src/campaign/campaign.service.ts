import { Injectable, NotFoundException, Logger } from '@nestjs/common';
import { eq, and, count, desc, sql } from 'drizzle-orm';
import { DatabaseService } from '../database/database.service';
import { campaigns } from './entities/campaign.entity';
import type { CreateCampaignDto } from './dto/create-campaign.dto';
import type { UpdateCampaignDto } from './dto/update-campaign.dto';

@Injectable()
export class CampaignService {
  private readonly logger = new Logger(CampaignService.name);

  constructor(private readonly database: DatabaseService) {}

  async create(dto: CreateCampaignDto) {
    const [campaign] = await this.database.db
      .insert(campaigns)
      .values({
        name: dto.name,
        description: dto.description ?? null,
      })
      .returning();
    this.logger.log(`Campaign created: ${campaign.id}`);
    return campaign;
  }

  async findAll(page = 1, limit = 10) {
    const offset = (page - 1) * limit;
    const whereClause = eq(campaigns.isDeleted, false);

    const [total, items] = await Promise.all([
      this.database.db
        .select({ total: count() })
        .from(campaigns)
        .where(whereClause)
        .then((r) => Number(r[0]?.total ?? 0)),
      this.database.db
        .select()
        .from(campaigns)
        .where(whereClause)
        .orderBy(desc(campaigns.createdAt))
        .limit(limit)
        .offset(offset),
    ]);

    return {
      items,
      meta: {
        total,
        page,
        limit,
        totalPages: Math.ceil(total / limit),
      },
    };
  }

  async findOne(id: string) {
    const whereClause = and(eq(campaigns.id, id), eq(campaigns.isDeleted, false));
    const [campaign] = await this.database.db
      .select()
      .from(campaigns)
      .where(whereClause)
      .limit(1);

    if (!campaign) {
      throw new NotFoundException(`Campaign with id "${id}" not found`);
    }
    return campaign;
  }

  async update(id: string, dto: UpdateCampaignDto) {
    await this.findOne(id);

    const [updated] = await this.database.db
      .update(campaigns)
      .set({
        ...dto,
        updatedAt: sql`now()`,
      })
      .where(and(eq(campaigns.id, id), eq(campaigns.isDeleted, false)))
      .returning();
    return updated;
  }

  async remove(id: string) {
    await this.findOne(id);

    await this.database.db
      .update(campaigns)
      .set({
        isDeleted: true,
        updatedAt: sql`now()`,
      })
      .where(eq(campaigns.id, id));
  }
}
