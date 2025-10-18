# Build stage
FROM node:18-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy source code and public assets
COPY . .

# Build the application
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built files from builder stage
COPY --from=builder /app/dist/ /usr/share/nginx/html/

# Copy nginx configuration  
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Remove default config
RUN rm -f /etc/nginx/conf.d/default.conf.default

# Expose port 8080
EXPOSE 8080

# Start nginx
CMD ["nginx", "-g", "daemon off;"]

