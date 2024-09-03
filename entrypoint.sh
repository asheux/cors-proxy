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
pipeninstall)
  pipenv install "$2"
  ;;
shell)
  bash
  ;;
init)
  wait_for_db
  flask db init
  flask db migrate
  flask db upgrade
  ;;
dropall)
  wait_for_db
  flask db downgrade base
  flask db migrate
  flask db upgrade
  ;;
runprodserver)
  wait_for_db
  flask db migrate
  flask db upgrade
  gunicorn --bind 0.0.0.0:5000 wsgi:app --workers=2 --preload
  ;;
rundevserver)
  wait_for_db
  flask db migrate
  flask db upgrade
  flask run --host=0.0.0.0 --port=5000 --debug
  ;;
python)
  shift 1
  python3 "$@"
  ;;
esac
