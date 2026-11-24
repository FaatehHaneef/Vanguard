# Build the site to static HTML, then serve the files with nginx. Only build/ is served.
FROM node:22-alpine AS build
WORKDIR /site
COPY package.json package-lock.json ./
RUN npm ci
COPY svelte.config.js vite.config.ts tsconfig.json ./
COPY static ./static
COPY src ./src
RUN npm run build

FROM nginx:1.27-alpine
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /site/build /usr/share/nginx/html
EXPOSE 3105
