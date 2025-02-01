from flask import Flask
from app.routes import register_blueprints
from app.extensions import db
from app.config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    register_blueprints(app)

    return app