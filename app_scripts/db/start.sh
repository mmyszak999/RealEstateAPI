#!/usr/bin/env sh

set -e

mysql_ready() {
    nc -z db 3306
}

until mysql_ready; do
  echo "MySQL is unavailable, waiting..."
  sleep 2
done

echo "MySQL connection established, continuing..."

exec "$@"
