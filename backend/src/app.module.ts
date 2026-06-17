import { Module } from '@nestjs/common';
import { LoggerModule } from 'nestjs-pino';
import { DatabaseModule } from './database/database.module';
import { CampaignModule } from './campaign/campaign.module';

@Module({
  imports: [
    LoggerModule.forRoot({
      pinoHttp: {
        transport:
          process.env.NODE_ENV !== 'production'
            ? {
                target: require.resolve('pino-pretty'),
                options: { colorize: true },
              }
            : undefined,
      },
    }),
    DatabaseModule,
    CampaignModule,
  ],
  controllers: [],
  providers: [],
})
export class AppModule {}
