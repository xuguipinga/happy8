# Build stage
FROM node:18-alpine as build-stage
WORKDIR /app
COPY package*.json ./
ENV NODE_OPTIONS="--max-old-space-size=512"
RUN npm config set registry https://registry.npmmirror.com && \
    npm config set fetch-retries 5 && \
    npm config set fetch-retry-factor 2 && \
    npm config set fetch-timeout 600000 && \
    npm ci --no-audit --no-fund
COPY . .
RUN npm run build

# Production stage
FROM nginx:stable-alpine as production-stage
COPY --from=build-stage /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
