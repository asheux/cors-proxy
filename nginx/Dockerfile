FROM nginx:latest

RUN apt-get update && apt-get upgrade -y && apt-get install -y \
        netcat-traditional python3-certbot-nginx

WORKDIR /nginx
# Copy the NGINX configuration directly into the image
COPY ./nginx-entrypoint.sh /usr/local/bin/nginx-entrypoint.sh
COPY ./nginx.conf /etc/nginx/nginx.conf
COPY ./nginx.conf /etc/nginx/conf.d/default.conf
RUN  mkdir -p ./nginx/www/certbot/.well-known/acme-challenge

RUN chmod +x /usr/local/bin/nginx-entrypoint.sh
EXPOSE 80
EXPOSE 443
ENTRYPOINT ["/usr/local/bin/nginx-entrypoint.sh"]
