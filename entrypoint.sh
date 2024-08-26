#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
# http://stackoverflow.com/questions/19622198/what-does-set-e-mean-in-a-bash-script
set -e

# Define help message
show_help() {
  echo """
    Entrypoint Commands Service:

    pipenv_install       : Add and install a dependency with pipenv
    shell                : Start a bash shell
    migrate              : Run migrations
    runserver            : Collect static files, run migrations and run the flask development server
    python [args...]     : Run internal python
"""
}

project_dir=/code

wait_for_db() {
  while ! nc -z "${DB_HOST}" "${DB_PORT}"; do
    echo "Waiting for DB to be ready"
    sleep 2
  done
}

case "$1" in
pipenv_install)
  pipenv install "$2"
  ;;
shell)
  bash
  ;;
migrate)
  wait_for_db
  python migrate.py
  ;;
runserver)
  wait_for_db
  python3 migrate.py
  gunicorn --bind 0.0.0.0:5000 wsgi:app --workers=2 --preload
  # flask run --host=0.0.0.0 --port=5000 --debug
  ;;
python)
  shift 1
  python3 "$@"
  ;;
esac
