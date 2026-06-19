ARG VITE_API_URL=""

FROM node:20-alpine AS builder
ARG VITE_API_URL
WORKDIR /app

RUN corepack enable && corepack prepare pnpm@9 --activate

COPY package.json pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile

COPY . .

RUN VITE_API_URL=${VITE_API_URL} pnpm build

FROM nginx:1.27-alpine AS production

RUN apk add --no-cache curl && \
    addgroup -S -g 1001 app && adduser -S -u 1001 -G app app

COPY nginx.conf /etc/nginx/nginx.conf

COPY --from=builder /app/dist /usr/share/nginx/html

RUN chown -R app:app /usr/share/nginx/html /var/cache/nginx /var/run && \
    chmod -R 755 /usr/share/nginx/html

USER app

EXPOSE 5173

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:5173/ || exit 1

CMD ["nginx", "-g", "daemon off;"]
