import os

from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS


def create_app():
    # Configuration
    load_dotenv()
    db_user = os.getenv('POSTGRES_USER')
    db_password = os.getenv('POSTGRES_PASSWORD')
    db_name = os.getenv('POSTGRES_DB')
    db_port = os.getenv('DB_PORT')
    db_host = os.getenv('DB_HOST')
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    CORS(app)
    return app

app = create_app()
