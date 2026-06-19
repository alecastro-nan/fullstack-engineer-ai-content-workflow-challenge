FROM node:20-alpine AS builder
WORKDIR /app

RUN corepack enable && corepack prepare pnpm@latest --activate

COPY package.json pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile

COPY . .

RUN pnpm build

FROM nginx:alpine AS production

RUN addgroup -S app && adduser -S -G app app

COPY nginx.conf /etc/nginx/conf.d/default.conf

COPY --from=builder /app/dist /usr/share/nginx/html

RUN chown -R app:app /usr/share/nginx/html && \
    chmod -R 755 /usr/share/nginx/html

USER app

EXPOSE 5173

CMD ["nginx", "-g", "daemon off;"]
