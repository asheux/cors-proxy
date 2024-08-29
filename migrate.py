import psycopg2
from psycopg2 import sql

from create_app import app

def migrate():
    from corsproxy.models import db
    with app.app_context():
        print('Running migrations...')
        db.create_all()

migrate()
