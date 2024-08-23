#!/usr/bin/env sh

mysql_ready () {
  nc -z -i 2 db 3306
}

until mysql_ready; do
  echo 'MySQL is unavailable, waiting...'
done

echo 'MySQL connection established, continuing...'

exec "$@"