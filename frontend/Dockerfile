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

RUN apk add --no-cache gettext

COPY --from=build /app/build/ /usr/share/nginx/html/

# Copy Railway template into a place we will render from
COPY nginx.conf.template /etc/nginx/templates/default.conf.template

# Keep local compose config, but NOT in conf.d (so Railway won't load it)
COPY nginx.conf /opt/nginx/nginx.conf.local

ENV API_UPSTREAM=http://localhost:8000/

CMD ["/bin/sh", "-c", "envsubst '$$PORT $$API_UPSTREAM' < /etc/nginx/templates/default.conf.template > /etc/nginx/conf.d/default.conf && nginx -g 'daemon off;'"]
