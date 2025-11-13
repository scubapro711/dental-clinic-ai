# Build stage
FROM node:20-alpine AS build

# Accept build arguments
ARG VITE_APP_ENV=production
ARG VITE_API_BASE_URL
ARG VITE_API_URL

# Set as environment variables for Vite build
ENV VITE_APP_ENV=$VITE_APP_ENV
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL
ENV VITE_API_URL=$VITE_API_URL

# Install pnpm
RUN npm install -g pnpm@latest

# Set working directory
WORKDIR /app

# Copy package files (pnpm uses pnpm-lock.yaml)
COPY package.json pnpm-lock.yaml ./

# Install dependencies with pnpm
RUN pnpm install --frozen-lockfile

# Copy source code
COPY . .

# Create .env.production file with build-time variables for Vite
# Vite will read this file during build and replace import.meta.env references
RUN echo "VITE_APP_ENV=$VITE_APP_ENV" > .env.production && \
    echo "VITE_API_URL=$VITE_API_URL" >> .env.production && \
    echo "=== Created .env.production ===" && \
    cat .env.production && \
    echo "==============================="

# Build the app with pnpm
# Vite will now correctly read VITE_API_URL from .env.production
RUN pnpm build

# Verify the build output
RUN echo "=== Build completed ===" && \
    ls -la /app/dist && \
    echo "======================="

# Production stage
FROM nginx:alpine

# Copy built files from build stage
COPY --from=build /app/dist /usr/share/nginx/html

# Copy nginx configuration template
# nginx:alpine automatically processes templates in /etc/nginx/templates/
COPY nginx.conf /etc/nginx/templates/default.conf.template

# Expose port 8080 (Cloud Run default)
EXPOSE 8080

# Set default PORT if not provided
# nginx entrypoint will automatically run envsubst on templates
ENV PORT=8080

# Use default nginx entrypoint (handles templates automatically)
# No need for custom entrypoint!

