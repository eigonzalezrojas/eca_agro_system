from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    @app.after_request
    def add_header(response):
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '-1'
        return response

    register_blueprints(app)

    return app

def register_blueprints(app):
    from app.routes import main, auth, dashboard

    app.register_blueprint(main)
    app.register_blueprint(auth)
    app.register_blueprint(dashboard)