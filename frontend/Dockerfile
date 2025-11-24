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

# Nginx config for SPA + API proxy
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy CRA build output
COPY --from=build /app/build/ /usr/share/nginx/html/

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
