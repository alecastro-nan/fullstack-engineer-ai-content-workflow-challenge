import {
  Controller,
  Get,
  Post,
  Patch,
  Delete,
  Body,
  Param,
  Query,
  ParseUUIDPipe,
  HttpCode,
} from '@nestjs/common';
import { CampaignService } from './campaign.service';
import { CreateCampaignDto } from './dto/create-campaign.dto';
import { UpdateCampaignDto } from './dto/update-campaign.dto';

@Controller('campaigns')
export class CampaignController {
  constructor(private readonly campaignService: CampaignService) {}

  @Post()
  create(@Body() dto: CreateCampaignDto) {
    return this.campaignService.create(dto);
  }

  @Get()
  findAll(
    @Query('page') page?: string,
    @Query('limit') limit?: string,
  ) {
    return this.campaignService.findAll(
      page ? Number(page) : 1,
      limit ? Number(limit) : 10,
    );
  }

  @Get(':id')
  findOne(@Param('id', ParseUUIDPipe) id: string) {
    return this.campaignService.findOne(id);
  }

  @Patch(':id')
  update(
    @Param('id', ParseUUIDPipe) id: string,
    @Body() dto: UpdateCampaignDto,
  ) {
    return this.campaignService.update(id, dto);
  }

  @Delete(':id')
  @HttpCode(204)
  remove(@Param('id', ParseUUIDPipe) id: string) {
    return this.campaignService.remove(id);
  }
}
