#!/bin/sh
set -e

cd /app

# Keep container node_modules in sync with mounted package-lock.json
npm ci

exec "$@"
