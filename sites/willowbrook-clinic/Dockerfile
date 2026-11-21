# Static site served by nginx. Only public/ is served; README and MANIFEST stay out.
FROM nginx:1.27-alpine
COPY public/ /usr/share/nginx/html/
RUN sed -i 's/listen  *80;/listen 3101;/' /etc/nginx/conf.d/default.conf
EXPOSE 3101
