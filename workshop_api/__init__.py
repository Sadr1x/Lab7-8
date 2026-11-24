import os

from flask import Flask
from flask_migrate import Migrate

from .models import db

migrate = Migrate(compare_server_default=True)


def create_app(config=None):
    app = Flask(__name__)
    app.config.from_mapping(
        SQLALCHEMY_DATABASE_URI=os.getenv("WORKSHOP_DB_URI", "sqlite:///workshop.sqlite3"),
    )
    if config is not None:
        app.config.update(config)
    os.makedirs(app.instance_path, exist_ok=True)
    db.init_app(app)
    migrate.init_app(app, db)

    from .routes import api

    app.register_blueprint(api)
    return app
