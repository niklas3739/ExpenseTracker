# ---- Build stage ----
FROM node:20-alpine AS build
WORKDIR /app

# Install deps
COPY package*.json ./
RUN npm install --no-audit --no-fund

# Copy sources and build
COPY . .
RUN npm run build

# ---- Runtime stage: Nginx ----
FROM nginx:1.27-alpine

# Install envsubst for template rendering
RUN apk add --no-cache gettext

# Copy CRA build output
COPY --from=build /app/build/ /usr/share/nginx/html/

# Copy both configs
COPY nginx.conf /etc/nginx/conf.d/nginx.local.conf
COPY nginx.conf.template /etc/nginx/templates/default.conf.template

# Default upstream (overridden on Railway)
ENV API_UPSTREAM=http://localhost:8000/

EXPOSE 8080

CMD ["/bin/sh", "-c", "envsubst '$$PORT $$API_UPSTREAM' < /etc/nginx/templates/default.conf.template > /etc/nginx/conf.d/default.conf && nginx -g 'daemon off;'"]
