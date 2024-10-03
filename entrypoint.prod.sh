#!/bin/sh

if [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for postgres..."

    while ! nc -z $POSTGRES_HOST $POSTGRES_PORT; do
      echo "PostgreSQL is unavailable - sleeping"
      sleep 0.1
    done

    echo "PostgreSQL started"
fi

exec "$@"