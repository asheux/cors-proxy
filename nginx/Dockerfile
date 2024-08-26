FROM nginx:latest

RUN apt-get update && apt-get upgrade -y && apt-get install -y netcat-traditional

WORKDIR /nginx
# Copy the NGINX configuration directly into the image
COPY ./nginx.conf /etc/nginx/nginx.conf
COPY ./nginx.conf /etc/nginx/conf.d/default.conf
COPY ./certificates /etc/nginx/certificates

RUN chmod +x /usr/local/bin/nginx-entrypoint.sh
EXPOSE 80
EXPOSE 443
