##### DEPENDENCIES

FROM node:20-alpine AS deps
RUN apk add --no-cache libc6-compat openssl
WORKDIR /app


# Install dependencies based on the preferred package manager

COPY package.json yarn.lock* package-lock.json* pnpm-lock.yaml* ./

RUN \
    if [ -f yarn.lock ]; then yarn --frozen-lockfile; \
    elif [ -f package-lock.json ]; then npm ci; \
    elif [ -f pnpm-lock.yaml ]; then npm install -g pnpm && pnpm i; \
    else echo "Lockfile not found." && exit 1; \
    fi

##### BUILDER

FROM node:20-alpine AS builder
RUN apk add --no-cache libc6-compat openssl
WORKDIR /app
ARG NEXT_PUBLIC_API_URL

# Copy dependencies from deps stage
COPY --from=deps /app/node_modules ./node_modules

# Copy package manager files (these change less frequently)
COPY package.json yarn.lock* package-lock.json* pnpm-lock.yaml* ./

# Copy configuration files (these change less frequently than source code)
COPY next.config.js tsconfig.json postcss.config.js prettier.config.js eslint.config.js components.json ./

# Copy public assets (these change less frequently than source code)
COPY public ./public

# Copy source code (this changes most frequently, so it's last)
COPY src ./src

ENV NEXT_TELEMETRY_DISABLED=1

RUN \
    if [ -f yarn.lock ]; then SKIP_ENV_VALIDATION=1 yarn build; \
    elif [ -f package-lock.json ]; then SKIP_ENV_VALIDATION=1 npm run build; \
    elif [ -f pnpm-lock.yaml ]; then npm install -g pnpm && SKIP_ENV_VALIDATION=1 pnpm run build; \
    else echo "Lockfile not found." && exit 1; \
    fi

##### RUNNER

# Using node:20-alpine as alternative to distroless (which requires gcr.io access)
# To use distroless, manually load the image: docker load -i distroless-nodejs20.tar
FROM node:20-alpine AS runner
RUN apk add --no-cache dumb-init
WORKDIR /app

ENV NODE_ENV=production

ENV NEXT_TELEMETRY_DISABLED=1

COPY --from=builder /app/next.config.js ./
COPY --from=builder /app/public ./public
COPY --from=builder /app/package.json ./package.json

COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static

EXPOSE 3001
ENV PORT=3001

# Use dumb-init for proper signal handling (similar to distroless behavior)
ENTRYPOINT ["dumb-init", "--"]
CMD ["node", "server.js"]
