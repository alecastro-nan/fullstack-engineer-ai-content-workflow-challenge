import { defineConfig } from 'vitest/config';
import swc from 'unplugin-swc';

export default defineConfig({
  plugins: [
    swc.vite({
      jsc: {
        parser: {
          syntax: 'typescript',
          decorators: true,
        },
        transform: {
          decoratorMetadata: true,
        },
      },
    }),
  ],
  test: {
    globals: true,
    environment: 'node',
    root: './',
    include: ['test/e2e/**/*.spec.ts', 'test/e2e/**/*.test.ts'],
    testTimeout: 15000,
    env: {
      DATABASE_URL: 'postgresql://postgres:postgres@localhost:5432/acme',
      NODE_ENV: 'test',
      PORT: '3001',
    },
  },
});
