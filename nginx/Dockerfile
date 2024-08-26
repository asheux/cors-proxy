FROM nginx:latest

WORKDIR /nginx
# Copy the NGINX configuration directly into the image
COPY ./nginx.conf /etc/nginx/nginx.conf
COPY ./nginx.conf /etc/nginx/conf.d/default.conf
COPY ./nginx-entrypoint.sh /usr/local/bin/nginx-entrypoint.sh
COPY ./certificates /etc/nginx/certificates

RUN chmod +x /usr/local/bin/nginx-entrypoint.sh
EXPOSE 80
EXPOSE 443

ENTRYPOINT ["/usr/local/bin/nginx-entrypoint.sh"]

