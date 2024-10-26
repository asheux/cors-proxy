#!/bin/sh
# Start NGINX

mkdir -p ./nginx/www/certbot/.well-known/acme-challenge
nginx -g "daemon off;"
