#!/bin/sh

# Wait for the corsproxy container to be available
echo "Waiting for DNS resolution of corsproxy..."
while ! nc -zv corsproxy 8000; do
  echo "corsproxy not available yet, sleeping..."
  sleep 2
done
echo "corsproxy is now available, starting nginx."

# Start NGINX
nginx -g "daemon off;"

