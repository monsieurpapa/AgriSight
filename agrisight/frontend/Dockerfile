# Frontend Dockerfile for AgriSight React Application

# Build stage
FROM node:20-alpine as build

WORKDIR /app

# Copy package files
COPY package*.json pnpm-lock.yaml ./

# Install pnpm and dependencies
RUN npm install -g pnpm
## The lockfile in the repo may be out-of-date with package.json (dev workflow or intentional pinning).
## Using --no-frozen-lockfile here allows the container build to succeed and regenerate/install
## packages according to package.json. In CI you may want to keep --frozen-lockfile and
## ensure pnpm-lock.yaml is kept in sync.
RUN pnpm install --no-frozen-lockfile

# Build-time env for Vite (must be set before build)
ARG VITE_API_BASE_URL=/
ARG VITE_WS_URL=
ENV VITE_API_BASE_URL=${VITE_API_BASE_URL}
ENV VITE_WS_URL=${VITE_WS_URL}
ENV VITE_API_URL=${VITE_API_BASE_URL}

# Copy source code
COPY . .

# Build the application
RUN pnpm run build

# Production stage
FROM nginx:alpine

# Copy built assets from build stage
COPY --from=build /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Install curl for healthcheck command
RUN apk add --no-cache curl

# Expose port 80
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost/ || exit 1

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
