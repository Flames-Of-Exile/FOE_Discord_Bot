#!/bin/sh

echo "Waiting for flask..."

while ! nc -z backend 5000; do
    sleep 0.1
done

echo "Flask started"

exec "$@"