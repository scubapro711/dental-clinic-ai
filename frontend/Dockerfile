# Build stage
FROM node:20-alpine AS build

# Accept build arguments
ARG VITE_APP_ENV=production
ARG VITE_API_BASE_URL

# Set as environment variables for Vite build
ENV VITE_APP_ENV=$VITE_APP_ENV
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL

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

# Build the app with pnpm
RUN pnpm build

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

