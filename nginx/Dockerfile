FROM nginx:latest

RUN apt-get update && apt-get upgrade -y && apt-get install -y \
        git gcc curl netcat-traditional curl libjpeg-dev \
        libgl1-mesa-glx ibglib2.0-0 libsm6 libxrender1 libxext6

WORKDIR /nginx
# Copy the NGINX configuration directly into the image
COPY ./nginx.conf /etc/nginx/nginx.conf
COPY ./nginx-entrypoint.sh /usr/local/bin/nginx-entrypoint.sh

RUN chmod +x /usr/local/bin/nginx-entrypoint.sh

ENTRYPOINT ["/usr/local/bin/nginx-entrypoint.sh"]

