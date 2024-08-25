import psycopg2
from psycopg2 import sql

from proxy import app, db, db_name, db_user, db_password, db_host, db_port


def create_database():
    conn = None
    try:
        conn = psycopg2.connect(
            dbname=db_name,
            user=db_user,
            password=db_password,
            host=db_host,
            port=db_port,
        )
        conn.autocommit = True
        cursor = conn.cursor()

        # Check if the database already exists
        cursor.execute(sql.SQL("SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s"), [db_name])
        exists = cursor.fetchone()

        if not exists:
            # Create the database if it doesn't exist
            cursor.execute(sql.SQL('CREATE DATABASE {}').format(sql.Identifier(db_name)))

        cursor.close()
    except Exception as error:
        print(f"Error creating database: {error}")
    finally:
        if conn is not None:
            conn.close()


with app.app_context():
    # db.drop_all()
    create_database()
    print('Running migrations...')
    db.create_all()
