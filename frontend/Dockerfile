# Production stage - use pre-built dist
FROM nginx:alpine

# Copy pre-built files
COPY dist/ /usr/share/nginx/html/

# Copy nginx configuration  
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Remove default config
RUN rm -f /etc/nginx/conf.d/default.conf.default

# Expose port 8080
EXPOSE 8080

# Start nginx
CMD ["nginx", "-g", "daemon off;"]

