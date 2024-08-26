#!/bin/sh

# Wait for the corsproxy container to be available
echo "Waiting for DNS resolution of corsproxy..."
while ! nc -zv app 5000; do
  echo "app service not available yet, sleeping..."
  sleep 2
done
echo "app service is now available, starting nginx."

# Start NGINX
nginx -g "daemon off;"

